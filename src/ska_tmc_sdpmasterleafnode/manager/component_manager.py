# pylint: disable= arguments-differ
"""
This module implements ComponentManager class for the Sdp Master Leaf Node.
"""
import logging
import threading
from logging import Logger
from typing import Callable, Optional, Tuple

from ska_control_model import AdminMode
from ska_ser_logging import configure_logging
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.base.base_component_manager import BaseComponentManager
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.v1.event_receiver import EventReceiver
from ska_tmc_common.v1.tmc_component_manager import TmcLeafNodeComponentManager
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
        sdp_master_admin_mode_enabled: bool,
        _update_admin_mode_callback: Callable,
        sdp_master_device_name: str,
        logger: Logger = LOGGER,
        _liveliness_probe: LivelinessProbeType = (
            LivelinessProbeType.SINGLE_DEVICE
        ),
        _event_receiver: bool = True,
        proxy_timeout: int = 500,
        event_subscription_check_period: int = 1,
        liveliness_check_period: int = 1,
        adapter_timeout: int = 30,
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
        :param proxy_timeout: Optional. Time period to wait for event and
        responses. Default 500 milliseconds
        :param adapter_timeout: Time period to wait for adapter creation
        :param sleep_time: Optional. Sleep time between reties. Default 1 Sec

        """

        self.sdp_master_device_name = sdp_master_device_name
        super().__init__(
            logger,
            _liveliness_probe=_liveliness_probe,
            _event_receiver=_event_receiver,
            proxy_timeout=proxy_timeout,
            event_subscription_check_period=event_subscription_check_period,
            liveliness_check_period=liveliness_check_period,
        )
        self._device: DeviceInfo = DeviceInfo(sdp_master_device_name)
        self._is_admin_mode_enabled: bool = sdp_master_admin_mode_enabled
        self.adapter_timeout = adapter_timeout
        self.update_availablity_callback = _update_availablity_callback
        self.update_admin_mode_callback = _update_admin_mode_callback
        self.on_command = On(self, logger)
        self.off_command = Off(self, logger)
        self.standby_command = Standby(self, logger)
        self.disable_command = Disable(self, logger)
        self.rlock = threading.RLock()

        if _event_receiver:
            evet_subscribe_check_period = event_subscription_check_period
            self._event_receiver = EventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                event_subscription_check_period=evet_subscribe_check_period,
                # attribute_dict=self.get_attribute_dict(),
                attribute_list=list(self.get_attribute_dict().keys()),
            )
            self._event_receiver.start()

        if _liveliness_probe:
            self.start_liveliness_probe(_liveliness_probe)

        self.event_processing_methods = self.get_attribute_dict()
        self.start_event_processing_threads()

    def get_attribute_dict(self) -> dict:
        """Returns the common attribute dictionary for all component types.

        :return: Dictionary of common attributes to be handled by
         the EventReceiver.

        """

        attributes = {
            "state": self.update_device_state,
            "healthState": self.update_device_health_state,
            "adminMode": self.update_device_admin_mode,
        }
        return {**attributes}

    @property
    def sdp_master_device_name(self) -> str:
        """Returns device name for the SDP Master Device.

        :return: sdp master fqdn string

        """

        return self._sdp_master_device_name

    @sdp_master_device_name.setter
    def sdp_master_device_name(self, device_name: str) -> None:
        """Sets the device name for SDP Master Device.

        :return: None

        """

        self._sdp_master_device_name = device_name

    def get_device(self) -> DeviceInfo:
        """Return the device info our of the monitoring loop
        with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo

        """

        return DeviceInfo(self.sdp_master_device_name)

    def _check_if_sdp_master_is_responsive(self) -> None:
        """Checks if SDP Master device is responsive."""

        if self._device is None or self._device.unresponsive:
            raise DeviceUnresponsive(
                f"{self.sdp_master_device_name} not available"
            )

    def is_command_allowed(self, command_name: str) -> bool:
        """Checks whether this command is allowed.
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

    def on(
        self, task_callback: Optional[TaskCallbackType] = None
    ) -> Tuple[TaskStatus, str]:
        """Submits the On command for execution.

        :rtype: tuple

        """

        task_status, response = self.submit_task(
            self.on_command.on,
            args=[self.logger],
            is_cmd_allowed=self._check_if_sdp_master_is_responsive(),
            task_callback=task_callback,
        )
        self.logger.debug(
            "Taskstatus: %s, Response: %s of On command:",
            task_status,
            response,
        )
        return task_status, response

    def off(
        self, task_callback: Optional[TaskCallbackType] = None
    ) -> Tuple[TaskStatus, str]:
        """Submits the Off command for execution.

        :rtype: tuple

        """

        task_status, response = self.submit_task(
            self.off_command.off,
            args=[self.logger],
            is_cmd_allowed=self._check_if_sdp_master_is_responsive(),
            task_callback=task_callback,
        )
        self.logger.debug(
            "Taskstatus: %s, Response: %s of Off command:",
            task_status,
            response,
        )
        return task_status, response

    def standby(
        self, task_callback: Optional[TaskCallbackType] = None
    ) -> Tuple[TaskStatus, str]:
        """Submits the Standby command for execution.

        :rtype: tuple

        """

        task_status, response = self.submit_task(
            self.standby_command.standby,
            args=[self.logger],
            is_cmd_allowed=self._check_if_sdp_master_is_responsive(),
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
            is_cmd_allowed=self._check_if_sdp_master_is_responsive(),
            task_callback=task_callback,
        )
        self.logger.info("Disable command queued for execution")
        return task_status, response

    def start_communicating(self: BaseComponentManager) -> None:
        """Establish communication with the component, then start monitoring.

        This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)
        """

    def stop_communicating(self: BaseComponentManager) -> None:
        """Cease monitoring the component, and break off all
        communication with it.

        For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.
        """

    def stop(self) -> None:
        """Stops the event processing"""
        self._event_receiver.stop()
        self._stop_thread = True

    def update_exception_for_unresponsiveness(
        self, device_info: DeviceInfo, exception: str
    ) -> None:
        """Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception

        """

        with self.rlock:
            device_info.update_unresponsive(True, exception)
            if self.update_availablity_callback is not None:
                self.update_availablity_callback(False)

    # pylint: disable=unused-argument
    def update_responsiveness_info(self, device_name: str = "") -> None:
        """Update a device with the correct availability information.

        :param dev_name: name of the device
        :type dev_name: str

        """
        with self.rlock:
            self.get_device().update_unresponsive(False, "")
            if self.update_availablity_callback is not None:
                self.update_availablity_callback(True)

    def update_device_admin_mode(self, admin_mode: AdminMode) -> None:
        """Update a monitored device admin mode,
          and call the relative callbacks if available

        :param device_name: Name of the device on which admin mode is updated
        :type device_name: str
        :param admin_state: admin mode of the device
        :type admin_mode: AdminMode

        """

        if self.is_admin_mode_enabled is True:
            super().update_device_admin_mode(admin_mode)
            self.logger.info(
                "Admin Mode value updated to :%s", AdminMode(admin_mode).name
            )
            if self.update_admin_mode_callback:
                self.update_admin_mode_callback(admin_mode)
