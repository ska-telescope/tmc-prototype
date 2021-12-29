import json
import threading

from ska_tango_base.control_model import HealthState, ObsState
from ska_tmc_centralnode.model.enum import ModesAvailability
from ska_tmc_common.device_info import DeviceInfo
from tango import DevState


class SdpsubarrayleafnodeComponent:
    """
    A component class for Sdpsubarrayleafnode Node

    It supports:

    * Maintaining a connection to its component

    * Monitoring its component
    """

    def __init__(self, logger):
        self._devices = []
        self.logger = logger
        self.lock = threading.Lock()  # needs to check, if required

    
    @property
    def devices(self):
        """
        Return the monitored devices.

        :return: the monitored devices
        :rtype: DeviceInfo[]
        """
        return self._devices

    def get_device(self, dev_name):
        """
        Return the monitored device info by name.

        :param dev_name: name of the device
        :return: the monitored device info
        :rtype: DeviceInfo
        """
        for devInfo in self.devices:
            if devInfo.dev_name == dev_name:
                return devInfo
        return None

    def remove_device(self, dev_name):
        """
        Remove a device from the list

        :param dev_name: name of the device
        """
        for devInfo in self.devices:
            if devInfo.dev_name == dev_name:
                self.devices.remove(devInfo)

    def update_device(self, devInfo):
        """
        Update (or add if missing) Device Information into the list of the component.

        :param devInfo: a DeviceInfo object
        """
        if devInfo not in self._devices:
            self._devices.append(devInfo)
        else:
            index = self._devices.index(devInfo)
            self._devices[index] = devInfo

        self._invoke_device_callback(devInfo)

    def update_device_exception(self, devInfo, exception):
        """
        Update (or add if missing) Device Information into the list of the component.

        :param devInfo: a DeviceInfo object
        """
        if devInfo not in self._devices:
            devInfo.update_unresponsive(True, exception)
            self._devices.append(devInfo)
            self._invoke_device_callback(devInfo)
        else:
            index = self._devices.index(devInfo)
            intDevInfo = self._devices[index]
            intDevInfo.state = DevState.UNKNOWN
            intDevInfo.update_unresponsive(True, exception)
            self._invoke_device_callback(intDevInfo)


class SdpSubArrayDeviceInfo(DeviceInfo):
    def __init__(self, dev_name, _unresponsive=False):
        super(SdpSubArrayDeviceInfo, self).__init__(dev_name, _unresponsive)
        self.obsState = ObsState.EMPTY

    def from_dev_info(self, sdpsubarrayDevInfo):
        super().from_dev_info(sdpsubarrayDevInfo)
        if isinstance(sdpsubarrayDevInfo, SdpSubArrayDeviceInfo):
            self.obsState = sdpsubarrayDevInfo.obsState

    def __eq__(self, other):
        if isinstance(other, SdpSubArrayDeviceInfo) or isinstance(
            other, DeviceInfo
        ):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        super_dict = super().to_dict()
        super_dict["obsState"] = str(ObsState(self.obsState))
        return super_dict
