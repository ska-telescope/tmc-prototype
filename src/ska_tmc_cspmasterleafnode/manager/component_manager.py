"""
This module implements ComponentManager class for the Csp Master Leaf Node.
"""
from ska_tmc_common.command_executor import CommandExecutor
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager


class CspMLNComponentManager(TmcLeafNodeComponentManager):
    """
    A component manager for The CSP Master Leaf Node component.

    It supports in controlling the behaviour of CSP Master.
    """

    def __init__(
        self,
        csp_master_dev_name,
        op_state_model,
        logger=None,
        _update_command_in_progress_callback=None,
        _monitoring_loop=False,
        _event_receiver=False,
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
            logger,
            _monitoring_loop,
            _event_receiver,
            max_workers,
            proxy_timeout,
            sleep_time,
        )

        self.update_device_info(csp_master_dev_name)
        self._command_executor = CommandExecutor(
            logger,
            _update_command_in_progress_callback=_update_command_in_progress_callback,
        )

    def update_device_info(self, csp_master_dev_name):
        self._csp_master_dev_name = csp_master_dev_name
        self._device = DeviceInfo(self._csp_master_dev_name, False)

    def device_failed(self, exception):
        """
        Set a device to failed and call the relative callback if available

        :param exception: an exception
        :type: Exception
        """
        with self.lock:
            self._device.exception = exception
