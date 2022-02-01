"""
This module implements ComponentManager class for the Sdp Master Leaf Node.
"""

import imp

# from ska_tmc_sdpmasterleafnode.manager.command_executor import CommandExecutor
from ska_tmc_common.command_executor import CommandExecutor
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.tmc_component_manager import TmcComponentManager

from ska_tmc_sdpmasterleafnode.model.component import SdpMLNComponent


class SdpMLNComponentManager(TmcComponentManager):
    """
    A component manager for The SDP Master Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    * Controlling the behaviour of SDP Master.
    """

    def __init__(
        self,
        op_state_model,
        _input_parameter,
        _component=None,
        logger=None,
        _update_device_callback=None,
        _update_command_in_progress_callback=None,
        _monitoring_loop=False,
        _event_receiver=True,
        max_workers=1,
        proxy_timeout=500,
        sleep_time=1,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param _component: Optional. Allows setting of the component to be
            managed; for testing purposes only
        :param logger: Optional. A logger for this component manager
        :param _monitoring_loop: Optional. Monitoring loop for the component manager
        :param _event_receiver: Optional. Object of EventReceiver class
        :param max_workers: Optional. Maximum worker threads for monitoring purpose. Default 1
        :param proxy_timeout: Optional. Time period to wait for event and responses. Default 500 milliseconds
        :param sleep_time: Optional. Sleep time between reties. Default 1 Sec
        """

        super().__init__(
            op_state_model,
            _component,
            logger,
            _monitoring_loop=False,
            _event_receiver=False,
            max_workers=5,
            proxy_timeout=500,
            sleep_time=1,
        )

        self.component = _component or SdpMLNComponent(logger)
        self.component.set_op_callbacks(_update_device_callback)
        self._input_parameter = _input_parameter
        self._command_executor = CommandExecutor(
            logger,
            _update_command_in_progress_callback=_update_command_in_progress_callback,
        )

    @property
    def input_parameter(self):
        """
        Return the input parameter

        :return: input parameter
        :rtype: InputParameter
        """
        return self._input_parameter

    @property
    def checked_devices(self):
        """
        Return the list of the checked monitored devices

        :return: list of the checked monitored devices
        """
        result = []
        for dev in self.component.devices:
            if dev.unresponsive:
                result.append(dev)
                continue
        return result

    def update_input_parameter(self):
        with self.lock:
            self.input_parameter.update(self)

    def add_device(self, dev_name):
        """
        Add device to the monitoring loop

        :param dev_name: device name
        :type dev_name: str
        """
        if dev_name is None:
            return

        devInfo = DeviceInfo(dev_name, False)

        self.component.update_device(devInfo)
