"""SDP Subarray Leaf Node Base Command Class for SDP Subarray Leaf Node"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

from ska_control_model.task_status import TaskStatus
from ska_ser_logging import configure_logging
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tmc_common import SdpSubArrayAdapter
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.exceptions import CommandNotAllowed
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import ConnectionFailed, DevFailed, DevState

if TYPE_CHECKING:
    from ..manager.component_manager import SdpSLNComponentManager
configure_logging()
LOGGER = logging.getLogger(__name__)


def task_callback_default(
    status: TaskStatus | None = None,
    progress: int | None = None,
    result: Any = None,
    exception: Exception | None = None,
) -> None:
    """
    Default method if the taskcallback is not passed

    :param status: status of the task.
    :param progress: progress of the task.
    :param result: result of the task.
    :param exception: an exception raised from the task.
    """
    LOGGER.warning(
        "This is default task callback."
        + "There is no action taken under this callback."
        + "Please provide task callback."
    )
    LOGGER.info(
        "long running command status: %s, progress: %s ,result:%s ,"
        + "exception %s",
        status,
        progress,
        result,
        exception,
    )


class SdpSLNCommand(TmcLeafNodeCommand):
    """SDP Subarray Leaf Node Class"""

    def __init__(
        self,
        component_manager: SdpSLNComponentManager,
        logger: logging.Logger = LOGGER,
    ) -> None:
        super().__init__(component_manager, logger=logger)
        self.component_manager = component_manager
        self.sdp_subarray_adapter = None
        self.task_callback: TaskCallbackType = task_callback_default

    def check_op_state(self, command_name) -> None:
        """Checks the operational state of the device"""
        if self.op_state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            raise CommandNotAllowed(
                "The invocation of the {} command on this".format(command_name)
                + "device is not allowed."
                + "Reason: The current operational state is"
                + "{}".format(self.op_state_model.op_state)
                + "The command has NOT been executed."
                + "This device will continue with normal operation."
            )

    def init_adapter(self) -> Tuple[ResultCode, str]:
        timeout = self.component_manager.timeout
        elapsed_time: float = 0
        start_time: float = time.time()
        device = self.component_manager._sdp_subarray_dev_name
        while self.sdp_subarray_adapter is None and elapsed_time < timeout:
            try:
                get_adapter = self.adapter_factory.get_or_create_adapter
                self.sdp_subarray_adapter: SdpSubArrayAdapter = get_adapter(
                    device,
                    AdapterType.SDPSUBARRAY,
                )
            except ConnectionFailed as connection_failed:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        "Error in creating adapter for %s : %s",
                        device,
                        connection_failed,
                    )
                    return ResultCode.FAILED, message
            except DevFailed as device_failed:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = (
                        "Error in creating adapter for %s : %s",
                        device,
                        device_failed,
                    )
                    return ResultCode.FAILED, message
            except (AttributeError, ValueError, TypeError) as exception:
                message = (
                    "Error in creating adapter for %s : %s",
                    device,
                    exception,
                )
                return ResultCode.FAILED, message
        return (ResultCode.OK, "")

    def update_task_status(
        self,
        **kwargs: Dict[str, Union[Tuple[ResultCode, str], TaskStatus, str]],
    ) -> None:
        """
        Update the status of a task.

        Args:
            **kwargs: Keyword arguments for task status update.
        """
        result = kwargs.get("result")
        status = kwargs.get("status", TaskStatus.COMPLETED)
        message = kwargs.get("exception")
        if status == TaskStatus.ABORTED:
            self.task_callback(status=status)
        if result:
            if result[0] == ResultCode.FAILED:
                self.task_callback(
                    status=status, result=result, exception=message
                )
            else:
                self.task_callback(status=status, result=result)
        self.component_manager.command_in_progress = ""

    def init_adapter_low(self):
        self.init_adapter()

    def init_adapter_mid(self):
        self.init_adapter()

    def do_mid(self, argin: Optional[Any] = None):
        """Abstract Method from TmcLeafNodeCommand is
            defined here but not utilized by this Class.

        Args:
            argin (_type_, optional): Accepts argument if required.
                Defaults to None.
        """

    def do_low(self, argin: Optional[Any] = None):
        """Abstract Method from TmcLeafNodeCommand is
            defined here but not utilized by this Class.

        Args:
            argin (_type_, optional): Accepts argument if required.
                Defaults to None.
        """

    def do(self, argin: Optional[Any] = None):
        """Abstract Method from TmcLeafNodeCommand is
            defined here but not utilized by this Class.

        Args:
            argin (_type_, optional): Accepts argument if required.
                Defaults to None.
        """
