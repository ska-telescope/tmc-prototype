# pylint: disable=, arguments-differ
"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import logging
import threading
import time
from typing import Callable, Optional, Tuple, Union

from ska_control_model import AdminMode
from ska_ser_logging import configure_logging
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.device_info import SubArrayDeviceInfo
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.exceptions import (
    CommandNotAllowed,
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_common.lrcr_callback import LRCRCallback
from ska_tmc_common.v1.tmc_component_manager import TmcLeafNodeComponentManager
from tango import DevState

from ska_tmc_sdpsubarrayleafnode.commands.abort_command import Abort
from ska_tmc_sdpsubarrayleafnode.commands.assign_resources_command import (
    AssignResources,
)
from ska_tmc_sdpsubarrayleafnode.commands.configure_command import Configure
from ska_tmc_sdpsubarrayleafnode.commands.end_command import End
from ska_tmc_sdpsubarrayleafnode.commands.end_scan_command import EndScan
from ska_tmc_sdpsubarrayleafnode.commands.off_command import Off
from ska_tmc_sdpsubarrayleafnode.commands.on_command import On
from ska_tmc_sdpsubarrayleafnode.commands.release_resources_command import (
    ReleaseAllResources,
)
from ska_tmc_sdpsubarrayleafnode.commands.restart_command import Restart
from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
from ska_tmc_sdpsubarrayleafnode.manager.event_receiver import (
    SdpSLNEventReceiver,
)

configure_logging()
LOGGER: logging.Logger = logging.getLogger(__name__)


class SdpSLNComponentManager(TmcLeafNodeComponentManager):
    """
    A component manager for The SDP Subarray Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(
        self,
        _update_admin_mode_callback: Callable,
        _sdp_subarray_admin_mode_enabled: bool,
        sdp_subarray_dev_name: str,
        _update_sdp_subarray_obs_state_callback: Callable,
        _update_lrcr_callback: Callable,
        _update_availablity_callback: Callable,
        _liveliness_probe: LivelinessProbeType = (
            LivelinessProbeType.SINGLE_DEVICE
        ),
        logger: logging.Logger = LOGGER,
        _event_receiver: bool = True,
        proxy_timeout: int = 500,
        event_subscription_check_period: int = 1,
        liveliness_check_period: int = 1,
        adapter_timeout: int = 30,
        command_timeout: int = 30,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        self._sdp_subarray_dev_name = sdp_subarray_dev_name
        super().__init__(
            logger,
            _liveliness_probe=_liveliness_probe,
            _event_receiver=False,
            proxy_timeout=proxy_timeout,
            event_subscription_check_period=event_subscription_check_period,
            liveliness_check_period=liveliness_check_period,
        )
        self._device: SubArrayDeviceInfo = SubArrayDeviceInfo(
            self._sdp_subarray_dev_name, False
        )

        if _liveliness_probe:
            self.start_liveliness_probe(_liveliness_probe)

        if _event_receiver:
            evt_subscription_check_period = event_subscription_check_period
            self.event_receiver = SdpSLNEventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                event_subscription_check_period=evt_subscription_check_period,
                attribute_list=list(self.get_attribute_dict().keys()),
            )
            self.event_receiver.start()
        self._update_availablity_callback = _update_availablity_callback
        self.adapter_timeout = adapter_timeout
        self.command_timeout = command_timeout
        self.rlock = threading.RLock()
        self.assign_id: str = ""
        self.configure_id: str = ""
        self.release_id: str = ""
        self.long_running_result_callback = LRCRCallback(self.logger)
        self._update_sdp_subarray_obs_state_callback = (
            _update_sdp_subarray_obs_state_callback
        )
        self.abort_event = threading.Event()
        self.update_lrcr_callback = _update_lrcr_callback
        self._lrc_result = ("", "")
        self.on_command = On(self, self.logger)
        self.off_command = Off(self, self.logger)
        self.command_in_progress: str = ""
        self.tracker_thread = None
        self._is_admin_mode_enabled: bool = _sdp_subarray_admin_mode_enabled
        self._update_admin_mode_callback = _update_admin_mode_callback
        self.event_processing_methods = self.get_attribute_dict()
        self.start_event_processing_threads()

    @property
    def lrc_result(self) -> Tuple[str, str]:
        """
        Returns the longRunningCommandResult attribute.

        :return: the longRunningCommandResult
        :rtype: spectrum
        """

        return self._lrc_result

    @lrc_result.setter
    def lrc_result(self, value: Tuple[str, str]) -> None:
        """
        Sets the longRunningCommandResult value

        :param value: the new longRunningCommandResult value
        :type value: str
        """
        if self._lrc_result != value:
            self._lrc_result = value
            self._invoke_lrcr_callback()

    def stop(self):
        """
        Method used to Stop the liveliness probe and event receiver
        for given devices.
        """
        self.stop_liveliness_probe()
        self.event_receiver.stop()
        self._stop_thread = True

    def get_device(self) -> SubArrayDeviceInfo:
        """
        Return the device info our of the monitoring loop with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def update_device_obs_state(self, obs_state: ObsState) -> None:
        """
        Update a monitored device obs state,
        and call the relative callbacks if available

        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """

        with self.rlock:
            dev_info = self.get_device()
            dev_info.obs_state = obs_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)
            self.logger.info(
                "Obs State value changed to :%s", ObsState(obs_state).name
            )
            if self._update_sdp_subarray_obs_state_callback:
                self._update_sdp_subarray_obs_state_callback(obs_state)
            self.observable.notify_observers(attribute_value_change=True)

    def update_exception_for_unresponsiveness(
        self, device_info: SubArrayDeviceInfo, exception: str
    ) -> None:
        """Set a device to failed and call the relative callback if available
        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        with self.rlock:
            device_info.update_unresponsive(True, exception)
            if self._update_availablity_callback is not None:
                self._update_availablity_callback(False)

    # pylint: disable=signature-differs
    # pylint: disable=unused-argument
    def update_responsiveness_info(self, device_name: str) -> None:
        """
        Update a device with the correct availability information.

        :param dev_name: name of the device
        :type dev_name: str
        """
        with self.rlock:
            self._device.update_unresponsive(False, "")
            if self._update_availablity_callback is not None:
                self._update_availablity_callback(True)

    def get_obs_state(self) -> ObsState:
        """
        Get Current device obsState
        """
        with self.rlock:
            return self.get_device().obs_state

    def update_command_result(self, command_name: str, value: str) -> None:
        """Updates the long running command result callback"""
        self.logger.info(
            "Received longRunningCommandResult for device : %s value: %s",
            self._sdp_subarray_dev_name,
            value,
        )
        try:
            # Ignoring ResultCode events
            int(value)
        except ValueError as value_error:
            self.logger.exception(
                f"Exception occurred in command {command_name}: {value_error}"
            )
            self.logger.info(
                f"Updating LRCRCallback with {value} for {command_name}"
            )
            self.long_running_result_callback(
                self.command_id, ResultCode.FAILED, exception_msg=value
            )
            self.observable.notify_observers(command_exception=True)

    def _invoke_lrcr_callback(self) -> None:
        """This method calls longRunningCommandResult callback"""
        if self.update_lrcr_callback is not None:
            self.update_lrcr_callback(self._lrc_result)

    def _check_if_sdp_sa_is_responsive(self) -> None:
        """Checks if SdpSubarray device is responsive."""

        if self._device is None or self._device.unresponsive:
            raise DeviceUnresponsive(f"{self._device} not available")

    def generate_command_result(
        self, result_code: ResultCode, message: str
    ) -> Tuple[ResultCode, str]:
        """This method is used for generating command result"""
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return result_code, message

    def raise_invalid_obsstate_error(
        self, command_name: str
    ) -> InvalidObsStateError:
        """
        checking the InvalidObsState of SdpSubarray device
        :param command_name: The name of command
        :type command_name: str
        """
        message = (
            f"{command_name} command is not allowed in current "
            + "observation state on device."
            + "Reason: The current observation state of "
            + f"{self._sdp_subarray_dev_name} "
            + f"for observation is {self.get_device().obs_state}\n"
            + f"The {command_name} command has NOT been executed. "
            + "This device will continue with normal operation."
        )
        raise InvalidObsStateError(message)

    def is_command_allowed_callable(self, command_name: str):
        """
        Args:
            command_name (str): _description_
        """
        self._check_if_sdp_sa_is_responsive()

        def check_obs_state():
            """Return whether the command may be called in the current state.

            Returns:
                bool: whether the command may be called in the current device
                state
            """
            match command_name:
                case "AssignResources":
                    if self.get_device().obs_state not in [
                        ObsState.EMPTY,
                        ObsState.IDLE,
                    ]:
                        return False
                case "ReleaseAllResources":
                    if self.get_device().obs_state != ObsState.IDLE:
                        return False
                case "Configure":
                    if self.get_device().obs_state not in [
                        ObsState.IDLE,
                        ObsState.READY,
                    ]:
                        return False
                case "End" | "Scan":
                    if self.get_device().obs_state != ObsState.READY:
                        return False
                case "EndScan":
                    if self.get_device().obs_state != ObsState.SCANNING:
                        return False
                case "Restart":
                    if self.get_device().obs_state not in [
                        ObsState.FAULT,
                        ObsState.ABORTED,
                    ]:
                        return False
            return True

        return check_obs_state

    def is_command_allowed(
        self, command_name: str
    ) -> Union[
        bool, InvalidObsStateError, DeviceUnresponsive, CommandNotAllowed
    ]:
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        if command_name == "Abort" and self.get_device().obs_state not in [
            ObsState.SCANNING,
            ObsState.CONFIGURING,
            ObsState.RESOURCING,
            ObsState.IDLE,
            ObsState.READY,
        ]:
            self.raise_invalid_obsstate_error(command_name)

        if self.op_state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            raise CommandNotAllowed(
                f"The invocation of the {command_name} command on this"
                + " device is not allowed."
                + "Reason: The current operational state is"
                + f"{self.op_state_model.op_state}"
                + "The command has NOT been executed. "
                + "This device will continue with normal operation."
            )
        return True

    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully
        invoked on SdpSubarray.

        :param event: a CmdDoneEvent object. This object is used to passdata
            to the callback method in asynchronous callback model forcommand
            execution.
        :type CmdDoneEvent object:
            It has the following members:
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to True if the command
                           failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext
        """

        if event.err:
            self.logger.error(
                "Error invoking command: %s failed with error : %s",
                event.cmd_name,
                event.errors,
            )

            error = event.errors[0]
            self.update_command_result(event.cmd_name, error.desc)

        else:
            self.logger.info(
                "Command %s invoked successfully.", event.cmd_name
            )

    # pylint: disable= signature-differs
    def on(self, task_callback: TaskCallbackType) -> Tuple[TaskStatus, str]:
        """Submits the On command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.on_command.on,
            args=[self.logger],
            is_cmd_allowed=self._check_if_sdp_sa_is_responsive(),
            task_callback=task_callback,
        )
        self.logger.info("On command queued for execution")
        return task_status, response

    def assign_resources(
        self, argin: str, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """
        Submit the AssignResources command in queue.

        :return: a result code and message
        """
        assign_resources_command = AssignResources(self, self.logger)
        self.assign_id = f"{time.time()}-{AssignResources.__name__}"
        task_status, response = self.submit_task(
            assign_resources_command.assign_resources,
            kwargs={"argin": argin},
            is_cmd_allowed=self.is_command_allowed_callable("AssignResources"),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of AssignResources "
                "command after being queued for execution"
            ),
            task_status,
            response,
        )
        return task_status, response

    def configure(
        self, argin: str, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """Submits the Configure command for execution.

        :rtype: tuple
        """
        configure_command = Configure(self, self.logger)
        self.configure_id = f"{time.time()}-{Configure.__name__}"
        task_status, response = self.submit_task(
            configure_command.configure,
            kwargs={"argin": argin},
            is_cmd_allowed=self.is_command_allowed_callable("Configure"),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of Configure "
                "command after being queued for execution"
            ),
            task_status,
            response,
        )
        return task_status, response

    def scan(
        self, argin: str, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """Submits the Scan command for execution.

        :rtype: tuple
        """
        scan_command = Scan(self, self.logger)
        task_status, response = self.submit_task(
            scan_command.scan,
            kwargs={"argin": argin},
            is_cmd_allowed=self.is_command_allowed_callable("Scan"),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of Scan command "
                "after being queued for execution"
            ),
            task_status,
            response,
        )
        return task_status, response

    # pylint: disable= signature-differs
    def off(self, task_callback: TaskCallbackType) -> Tuple[TaskStatus, str]:
        """Submits the Off command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.off_command.off,
            args=[self.logger],
            is_cmd_allowed=self._check_if_sdp_sa_is_responsive(),
            task_callback=task_callback,
        )
        self.logger.info("Off command queued for execution")
        return task_status, response

    def release_all_resources(
        self, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """Submits the ReleaseAllResources command for execution.

        :rtype: tuple
        """
        release_command = ReleaseAllResources(self, self.logger)
        self.release_id = f"{time.time()}-{ReleaseAllResources.__name__}"
        task_status, response = self.submit_task(
            release_command.release_resources,
            is_cmd_allowed=self.is_command_allowed_callable(
                "ReleaseAllResources"
            ),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of ReleaseAllResources "
                "command after being queued for execution"
            ),
            task_status,
            response,
        )
        return task_status, response

    def end(self, task_callback: TaskCallbackType) -> Tuple[TaskStatus, str]:
        """Submits the End command for execution.

        :rtype: tuple
        """
        end_command = End(self, self.logger)
        task_status, response = self.submit_task(
            end_command.end,
            args=[self.logger],
            is_cmd_allowed=self.is_command_allowed_callable("End"),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of End command "
                "after being queued for execution"
            ),
            task_status,
            response,
        )

        return task_status, response

    def end_scan(
        self, task_callback: TaskCallbackType
    ) -> Tuple[TaskStatus, str]:
        """Submits the EndScan command for execution.

        :rtype: tuple
        """
        end_scan_command = EndScan(self, self.logger)
        task_status, response = self.submit_task(
            end_scan_command.end_scan,
            args=[self.logger],
            is_cmd_allowed=self.is_command_allowed_callable("EndScan"),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of EndScan command "
                "after being queued for execution"
            ),
            task_status,
            response,
        )

        return task_status, response

    def abort_commands(self) -> Tuple[ResultCode, str]:
        """
        Invokes Abort command on Sdp Subarray
        and changes the obsstate

        :param task_callback: callback to be called whenever the status
            of the task changes.
        """
        abort_command = Abort(
            self,
            logger=self.logger,
        )
        self.abort_event.set()
        self.observable.notify_observers(attribute_value_change=True)
        result_code, message = abort_command.do()
        self.abort_event.clear()
        self.logger.info("Abort Event cleared")
        return result_code, message

    def restart(
        self, task_callback: Optional[TaskCallbackType] = None
    ) -> Tuple[TaskStatus, str]:
        """
        Submit the Restart command in queue.

        :return: a result code and message
        """
        restart_command = Restart(self, logger=self.logger)
        task_status, response = self.submit_task(
            restart_command.restart,
            args=[self.logger],
            is_cmd_allowed=self.is_command_allowed_callable("Restart"),
            task_callback=task_callback,
        )
        self.logger.info(
            (
                "TaskStatus: %s and Response: %s of Restart command "
                "after being queued for execution"
            ),
            task_status,
            response,
        )

        return task_status, response

    def standby(self, task_callback: Optional[Callable] = None) -> None:
        """
        Standby command is not implemented by SDP Subarray Leaf Node device.
        """

    def start_communicating(self: TmcLeafNodeComponentManager) -> None:
        """
        Establish communication with the component, then start monitoring.

        This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)
        """

    def stop_communicating(self: TmcLeafNodeComponentManager) -> None:
        """
        Cease monitoring the component, and break off all
        communication with it.

        For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.
        """

    def update_device_admin_mode(self, admin_mode: AdminMode) -> None:
        """
        Update a monitored device admin mode,
        and call the relative callbacks if available
        :param admin_state: admin mode of the device
        :type admin_mode: AdminMode
        """
        if self._is_admin_mode_enabled is True:
            super().update_device_admin_mode(admin_mode)
            self.logger.info(
                "Admin Mode value updated to :%s", AdminMode(admin_mode).name
            )
            if self._update_admin_mode_callback:
                self._update_admin_mode_callback(admin_mode)

    def get_attribute_dict(self) -> dict:
        """

        :return: Dictionary of attributes to be handled by the EventReceiver.
        """

        attributes = {
            "obsState": self.update_device_obs_state,
            "state": self.update_device_state,
            "healthState": self.update_device_health_state,
        }
        if self.is_admin_mode_enabled:
            attributes["adminMode"] = self.update_device_admin_mode

        return {**attributes}
