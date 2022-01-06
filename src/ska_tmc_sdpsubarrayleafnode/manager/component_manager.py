"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""

from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo
from ska_tmc_common.tmc_component_manager import TmcComponentManager

from ska_tmc_sdpsubarrayleafnode.model.component import SdpSLNComponent


class SdpSLNComponentManager(TmcComponentManager):
    """
    A component manager for The SDP Subarray Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(
        self,
        op_state_model,
        _input_parameter,
        logger=None,
        _component=None,
        _update_device_callback=None,
        _monitoring_loop=False,
        _event_receiver=False,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        super(SdpSLNComponentManager, self).__init__(
            op_state_model,
            _component,
            logger,
            _monitoring_loop,
            _event_receiver,
            max_workers,
            proxy_timeout,
            sleep_time,
        )

        self.component = _component or SdpSLNComponent(logger)

        self.component.set_op_callbacks(_update_device_callback)
        self._input_parameter = _input_parameter

    def stop(self):
        self._command_executor.stop()

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

    @property
    def command_in_progress(self):
        return self._command_executor.command_in_progress

    @property
    def command_executor(self):
        return self._command_executor

    @property
    def command_executed(self):
        return self._command_executor._command_executed

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

        if "subarray" in dev_name.lower():
            devInfo = SubArrayDeviceInfo(dev_name, False)
        else:
            devInfo = DeviceInfo(dev_name, False)

        self.component.update_device(devInfo)
