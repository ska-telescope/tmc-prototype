# pylint: disable= arguments-differ
"""
This module implements ComponentManager class for the Sdp Master Leaf Node.
"""
import logging
from logging import Logger
from typing import Callable, Optional, Tuple

from ska_ser_logging import configure_logging
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager
from tango import DevState

from ska_tmc_sdpmasterleafnode.commands import Disable, Off, On, Standby

configure_logging()
LOGGER = logging.getLogger(__name__)


class SdpMLNComponentManager(TmcLeafNodeComponentManager):
    """
    A component manager for The SDP Master Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    * Controlling the behaviour of SDP Master.
    """

    def __init__(
        self,
        sdp_master_device_name: str,
        logger: Logger = LOGGER,
        _liveliness_probe: LivelinessProbeType = (
            LivelinessProbeType.SINGLE_DEVICE
        ),
        _event_receiver: bool = False,
        max_workers: int = 1,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
        timeout: int = 30,
        _update_availablity_callback: Optional[Callable[[bool], None]] = None,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param _component: Optional. Allows setting of the component to be
            managed; for testing purposes only
        :param logger: Optional. A logger for this component manager
        :param _monitoring_loop: Optional. Monitoring loop for the component
        manager
        :param _event_receiver: Optional. Object of EventReceiver class
        :param max_workers: Optional. Maximum worker threads for monitoring
        purpose. Default 1
        :param proxy_timeout: Optional. Time period to wait for event and
        responses. Default 500 milliseconds
        :param sleep_time: Optional. Sleep time between reties. Default 1 Sec
        """
        self.sdp_master_device_name = sdp_master_device_name
        super().__init__(
            logger,
            _liveliness_probe=_liveliness_probe,
            _event_receiver=False,
            max_workers=max_workers,
            proxy_timeout=proxy_timeout,
            sleep_time=sleep_time,
        )
        self._device: DeviceInfo = DeviceInfo(sdp_master_device_name)

        self.timeout = timeout
        self.update_availablity_callback = _update_availablity_callback
        self.on_command = On(self, logger)
        self.off_command = Off(self, logger)
        self.standby_command = Standby(self, logger)
        self.disable_command = Disable(self, logger)

        if _liveliness_probe:
            self.start_liveliness_probe(_liveliness_probe)

    @property
    def sdp_master_device_name(self) -> str:
        """Returns device name for the SDP Master Device."""
        return self._sdp_master_device_name

    @sdp_master_device_name.setter
    def sdp_master_device_name(self, device_name: str) -> None:
        """Sets the device name for SDP Master Device."""
        self._sdp_master_device_name = device_name

    def get_device(self) -> DeviceInfo:
        """
        Return the device info our of the monitoring loop with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo
        """
        return DeviceInfo(self.sdp_master_device_name)

    def update_ping_info(self, ping: int, device_name: str) -> None:
        """
        Update a device with the correct ping information.
        :param ping: device response time
        :type ping: int
        """
        self.logger.debug("Updating ping info for device: %s", device_name)
        with self.lock:
            self._device.ping = ping
            self._device.update_unresponsive(False)
            if self.update_availablity_callback is not None:
                self.logger.info(
                    "Calling update_availablity_callback from update_ping_info"
                )
                self.update_availablity_callback(True)

    def update_device_ping_failure(
        self, device_info: DeviceInfo, exception: str
    ) -> None:  # pylint: disable=arguments-differ
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception"""
        device_info.update_unresponsive(True, exception)

        with self.lock:
            if self.update_availablity_callback is not None:
                self.update_availablity_callback(False)

    def _check_if_sdp_master_is_responsive(self) -> None:
        """Checks if SDP Master device is responsive."""

        if self._device is None or self._device.unresponsive:
            raise DeviceUnresponsive(
                f"{self.sdp_master_device_name} not available"
            )

    def is_command_allowed(self, command_name: str) -> bool:
        """
        Checks whether this command is allowed.
        It checks that the device is not in the FAULT and UNKNOWN state
        before executing the command and that all the
        components needed for the operation are not unresponsive.

        :return: True if this command is allowed

        :rtype: boolean
        """

        if command_name in ["On", "Off", "Standby", "Disable"]:
            if self.op_state_model.op_state in [
                DevState.FAULT,
                DevState.UNKNOWN,
            ]:
                raise CommandNotAllowed(
                    "The invocation of the {} command on this".format(
                        command_name
                    )
                    + "device is not allowed."
                    + "Reason: The current operational state is"
                    + "{}".format(self.op_state_model.op_state)
                    + "The command has NOT been executed."
                    + "This device will continue with normal operation."
                )
            self._check_if_sdp_master_is_responsive()
            return True
        return False

    # pylint: disable = signature-differs #The signature is different what is present in base classes and what is present at our end.
    
    def on(self, task_callback: TaskCallbackType) -> Tuple[TaskStatus, str]:
        """Submits the On command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.on_command.on,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.debug(
            "Taskstatus: %s, Response: %s of On command:",
            task_status,
            response,
        )
        return task_status, response

    # pylint: disable = signature-differs
    def off(self, task_callback: TaskCallbackType) -> Tuple[TaskStatus, str]:
        """Submits the Off command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.off_command.off,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.debug(
            "Taskstatus: %s, Response: %s of Off command:",
            task_status,
            response,
        )
        return task_status, response

    # pylint: disable = signature-differs
    def standby(
        self, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """Submits the Standby command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.standby_command.standby,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("Standby command queued for execution")
        return task_status, response

    def disable(
        self, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """Submits the Disable command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.disable_command.disable,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("Disable command queued for execution")
        return task_status, response

    def start_communicating(self: BaseComponentManager) -> None:
        """
        Establish communication with the component, then start monitoring.

        This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)
        """

    def stop_communicating(self: BaseComponentManager) -> None:
        """
        Cease monitoring the component, and break off all
        communication with it.

        For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.
        """
