# pylint: disable=no-member, arguments-renamed, arguments-differ
# pylint: disable=abstract-method
"""
This module provided a reference implementation of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import time
from typing import Callable, Optional, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.device_info import SubArrayDeviceInfo
from ska_tmc_common.exceptions import (
    CommandNotAllowed,
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_common.lrcr_callback import LRCRCallback
from ska_tmc_common.tmc_component_manager import TmcLeafNodeComponentManager
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
from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
from ska_tmc_sdpsubarrayleafnode.manager.event_receiver import (
    SdpSLNEventReceiver,
)


class SdpSLNComponentManager(TmcLeafNodeComponentManager):
    """
    A component manager for The SDP Subarray Leaf Node component.

    It supports:

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(
        self,
        sdp_subarray_dev_name,
        logger=None,
        communication_state_callback=None,
        component_state_callback=None,
        _liveliness_probe=None,
        _event_receiver=True,
        _update_sdp_subarray_obs_state_callback=None,
        _update_lrcr_callback=None,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
        timeout=30,
        _update_availablity_callback=None,
        command_timeout: int = 15,
    ):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        self._device = None
        self.update_availablity_callback = _update_availablity_callback
        super().__init__(
            logger,
            _liveliness_probe=_liveliness_probe,
            _event_receiver=False,
            communication_state_callback=communication_state_callback,
            component_state_callback=component_state_callback,
            max_workers=max_workers,
            proxy_timeout=proxy_timeout,
            sleep_time=sleep_time,
        )

        self._sdp_subarray_dev_name = sdp_subarray_dev_name
        self._device = SubArrayDeviceInfo(self._sdp_subarray_dev_name, False)

        if _event_receiver:
            self.event_receiver = SdpSLNEventReceiver(
                self,
                logger,
                proxy_timeout=proxy_timeout,
                sleep_time=sleep_time,
            )
            self.event_receiver.start()
        self._update_availablity_callback = _update_availablity_callback
        self.timeout = timeout
        self.command_timeout = command_timeout
        self.assign_id = None
        self.long_running_result_callback = LRCRCallback(self.logger)
        self._update_sdp_subarray_obs_state_callback = (
            _update_sdp_subarray_obs_state_callback
        )

        self.update_lrcr_callback = _update_lrcr_callback
        self._lrc_result = ("", "")
        self.on_command = On(self, self.logger)
        self.off_command = Off(self, self.logger)

    def stop(self):
        """
        Method used to Stop the liveliness probe and event receiver
        for given devices.
        """
        self.stop_liveliness_probe()
        self._event_receiver.stop()

    def get_device(self):
        """
        Return the device info our of the monitoring loop with name dev_name

        :param None:
        :return: a device info
        :rtype: DeviceInfo
        """
        return self._device

    def update_input_parameter(self):
        """Update input parameter"""
        with self.lock:
            self.input_parameter.update(self)

    def update_event_failure(self):
        """Update event failures"""
        with self.lock:
            dev_info = self.get_device()
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)

    def update_device_obs_state(self, obs_state):
        """
        Update a monitored device obs state,
        and call the relative callbacks if available

        :param dev_name: name of the device
        :type dev_name: str
        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """
        self.logger.info(f"Obs State value {obs_state}")
        with self.lock:
            dev_info = self.get_device()
            dev_info.obs_state = obs_state
            dev_info.last_event_arrived = time.time()
            dev_info.update_unresponsive(False)
            self.logger.info(f"Obs State value updated to {obs_state}")
            if self._update_sdp_subarray_obs_state_callback:
                self._update_sdp_subarray_obs_state_callback(obs_state)

    def device_failed(
        self, device_info, exception
    ):  # pylint: disable=arguments-differ
        """
        Set a device to failed and call the relative callback if available

        :param device_info: a device info
        :type device_info: DeviceInfo
        :param exception: an exception
        :type: Exception
        """
        device_info.update_unresponsive(True, exception)

        with self.lock:
            if self._update_availablity_callback is not None:
                self._update_availablity_callback(False)

    def update_ping_info(self, ping: int, dev_name: str) -> None:
        """
        Update a device with the correct ping information.

        :param dev_name: name of the device
        :type dev_name: str
        :param ping: device response time
        :type ping: int
        """
        with self.lock:
            self._device.ping = ping
            self._device.update_unresponsive(False)
            if self._update_availablity_callback is not None:
                self._update_availablity_callback(True)

    def get_obs_state(self) -> ObsState:
        """
        Get Current device obsState
        """
        return self.get_device().obs_state

    def update_command_result(self, command_name, value: str):
        """Updates the long running command result callback"""
        self.logger.info(
            "Recieved longRunningCommandResult event with value: %s",
            value,
        )
        try:
            # Ignoring ResultCode events
            int(value)
        except ValueError:
            if command_name == "AssignResources":
                self.logger.info(
                    "Updating LRCRCallback with value: %s for Assign",
                    value,
                )
                self.long_running_result_callback(
                    self.assign_id, ResultCode.FAILED, exception_msg=value
                )

    @property
    def lrc_result(self) -> tuple[str, str]:
        """
        Returns the longRunningCommandResult attribute.

        :return: the longRunningCommandResult
        :rtype: spectrum
        """
        return self._lrc_result

    @lrc_result.setter
    def lrc_result(self, value: str) -> None:
        """
        Sets the longRunningCommandResult value

        :param value: the new longRunningCommandResult value
        :type value: str
        """
        if self._lrc_result != value:
            self._lrc_result = value
            self._invoke_lrcr_callback()

    def _invoke_lrcr_callback(self):
        """This method calls longRunningCommandResult callback"""
        if self.update_lrcr_callback is not None:
            self.update_lrcr_callback(self._lrc_result)

    def _check_if_sdp_sa_is_responsive(self) -> None:
        """Checks if SdpSubarray device is responsive."""
        if self._device is None or self._device.unresponsive:
            raise DeviceUnresponsive(f"{self._device} not available")

    def generate_command_result(self, result_code, message):
        """This method is used for generating command result"""
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return result_code, message

    def raise_invalid_obsstate_error(self, command_name: str):
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

    def is_command_allowed(self, command_name: str):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        if self.op_state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            raise CommandNotAllowed(
                f"The invocation of the {command_name} command on this"
                + " device is not allowed."
                + "Reason: The current operational state is"
                + f"{self.op_state_model.op_state}"
                + "The command has NOT been executed. "
                + "This device will continue with normal operation."
            )

        self._check_if_sdp_sa_is_responsive()

        if command_name in [
            "AssignResources",
            "ReleaseAllResources",
        ]:
            # Checking obsState of Sdp Subarray device
            if self.get_device().obs_state not in [
                ObsState.IDLE,
                ObsState.EMPTY,
            ]:
                self.raise_invalid_obsstate_error(command_name)
        if command_name in ["Configure", "End"]:
            if self.get_device().obs_state not in [
                ObsState.IDLE,
                ObsState.READY,
            ]:
                self.raise_invalid_obsstate_error(command_name)

        if command_name == "Scan":
            if self.get_device().obs_state != ObsState.READY:
                self.raise_invalid_obsstate_error(command_name)

        if command_name == "EndScan":
            if self.get_device().obs_state != ObsState.SCANNING:
                self.raise_invalid_obsstate_error(command_name)

        elif command_name == "Abort":
            if self.get_device().obs_state not in [
                ObsState.SCANNING,
                ObsState.CONFIGURING,
                ObsState.RESOURCING,
                ObsState.IDLE,
                ObsState.READY,
            ]:
                self.raise_invalid_obsstate_error(command_name)

        return True

    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully
        invoked on SdpSubarray.

        :param event: a CmdDoneEvent object. This object is used to passdata
            to the callback method in asynchronous callback model forcommand
            execution.
        :type: CmdDoneEvent object
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
            log_message = (
                f"Error ininvoking command:{event.cmd_name}\n{event.errors}"
            )
            self.logger.error(log_message)
            error = event.errors[0]
            self.update_command_result(event.cmd_name, error.desc)

        else:
            log_message = f"Command {event.cmd_name} invoked successfully."
            self.logger.info(log_message)

    def on(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the On command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.on_command.on,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("On command queued for execution")
        return task_status, response

    def assign_resources(
        self, argin: str, task_callback: Optional[Callable] = None
    ) -> tuple:
        """
        Submit the AssignResources command in queue.

        :return: a result code and message
        """
        assign_resources_command = AssignResources(self, self.logger)
        self.assign_id = f"{time.time()}-{AssignResources.__name__}"
        task_status, response = self.submit_task(
            assign_resources_command.assign_resources,
            args=[argin],
            task_callback=task_callback,
        )
        return task_status, response

    def configure(
        self, argin: str, task_callback: Optional[Callable] = None
    ) -> Tuple[TaskStatus, str]:
        """Submits the Configure command for execution.

        :rtype: tuple
        """
        configure_command = Configure(self, self.logger)
        task_status, response = self.submit_task(
            configure_command.configure,
            args=[argin, self.logger],
            task_callback=task_callback,
        )
        self.logger.info(
            "TaskStatus: %s and Response: %s of Configure \
                  command after queued to execution",
            task_status,
            response,
        )
        return task_status, response

    def scan(
        self, argin: str, task_callback: Optional[Callable] = None
    ) -> Tuple[TaskStatus, str]:
        """Submits the Scan command for execution.

        :rtype: tuple
        """
        scan_command = Scan(self, self.logger)
        task_status, response = self.submit_task(
            scan_command.scan,
            args=[argin, self.logger],
            task_callback=task_callback,
        )
        self.logger.info(
            "TaskStatus: %s and Response: %s of Scan \
                  command after queued to execution",
            task_status,
            response,
        )
        return task_status, response

    def off(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the Off command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.off_command.off,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("Off command queued for execution")
        return task_status, response

    def release_all_resources(
        self, task_callback=None
    ) -> Tuple[TaskStatus, str]:
        """Submits the ReleaseAllResources command for execution.

        :rtype: tuple
        """
        release_command = ReleaseAllResources(self, self.logger)
        task_status, response = self.submit_task(
            release_command.release_resources,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info(
            "TaskStatus: %s and Response: %s of ReleaseAllResource \
                  command after queued to execution",
            task_status,
            response,
        )
        return task_status, response

    def end(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the End command for execution.

        :rtype: tuple
        """
        end_command = End(self, self.logger)
        task_status, response = self.submit_task(
            end_command.end,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info(
            "TaskStatus: %s and Response: %s of End command after queued\
                 to execution",
            task_status,
            response,
        )
        return task_status, response

    def end_scan(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the EndScan command for execution.

        :rtype: tuple
        """
        end_scan_command = EndScan(self, self.logger)
        task_status, response = self.submit_task(
            end_scan_command.end_scan,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info(
            "TaskStatus: %s and Response: %s of EndScan command after queued\
                 to execution",
            task_status,
            response,
        )
        return task_status, response

    def abort_commands(self, task_callback: Callable = None):
        """
        Invokes Abort command on lower level Csp Subarray
        and changes the obsstate

        :param task_callback: callback to be called whenever the status
            of the task changes.
        """
        abort_command = Abort(
            self,
            logger=self.logger,
        )
        result_code, message = abort_command.invoke_abort()
        return result_code, message
