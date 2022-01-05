from ska_tmc_common.tmc_component_manager import TmcComponent
from tango import DevState


class SdpSLNComponent(TmcComponent):
    """
    A component class for Sdpsubarrayleafnode Node

    It supports:

    * Maintaining a connection to its component

    * Monitoring its component
    """

    def __init__(self, logger):
        super(SdpSLNComponent, self).__init__(logger)
        self._devices = []
        # self.logger = logger
        self._update_device_callback = None
        # self.lock = threading.Lock()  # needs to check, if required

    def set_op_callbacks(
        self,
        _update_device_callback=None,
    ):
        self._update_device_callback = _update_device_callback

    def _invoke_device_callback(self, devInfo):
        if self._update_device_callback is not None:
            self._update_device_callback(devInfo)

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
