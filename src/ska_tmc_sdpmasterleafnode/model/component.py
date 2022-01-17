import json

from ska_tmc_common.tmc_component_manager import (
    TmcComponent,  # , dev_state_2_str
)
from tango import DevState


class SdpMLNComponent(TmcComponent):
    """
    A component class for Sdpmasterleafnode

    It supports:

    * Maintaining monitoring data of Sdp Master

    * Monitoring its component
    """

    def __init__(self, logger) -> None:
        super().__init__(logger)
        self._update_device_callback = None

    @property
    def devices(self):
        """
        Return the list of monitored devices.

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

    def update_device_exception(self, device_info, exception):
        """
        Update (or add if missing) Device Information into the list of the component.

        :param devInfo: a DeviceInfo object
        """
        if device_info not in self._devices:
            device_info.update_unresponsive(True, exception)
            self._devices.append(device_info)
            self._invoke_device_callback(device_info)
        else:
            index = self._devices.index(device_info)
            intDevInfo = self._devices[index]
            intDevInfo.state = DevState.UNKNOWN
            intDevInfo.update_unresponsive(True, exception)
            self._invoke_device_callback(intDevInfo)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        devices = []
        for dev in self.devices:
            devices.append(dev.to_dict())
        result = {
            "devices": devices,
        }

        return result
