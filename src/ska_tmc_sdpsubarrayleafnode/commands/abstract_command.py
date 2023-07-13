# pylint: disable=no-member
# pylint: disable=abstract-method
"""Abstract Command for SDP Subarray Leaf Node"""
import time

from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.exceptions import CommandNotAllowed, DeviceUnresponsive
from ska_tmc_common.tmc_command import TmcLeafNodeCommand
from tango import ConnectionFailed, DevFailed, DevState


class SdpSLNCommand(TmcLeafNodeCommand):
    """SDP Subarray Leaf Node Class"""

    def __init__(
        self,
        component_manager,
        logger=None,
    ) -> None:
        super().__init__(component_manager, logger=logger)
        self.component_manager = component_manager
        self.sdp_subarray_adapter = None

    def check_unresponsive(self):
        """Checks whether the device is unresponsive"""
        dev_info = self.component_manager.get_device()
        if dev_info is None or dev_info.unresponsive:
            raise DeviceUnresponsive(
                """The invocation of the command on this device is not allowed.
                Reason: SDP subarray device is not available.
                The command has NOT been executed.
                This device will continue with normal operation."""
            )

    def check_op_state(self, command_name):
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

    def init_adapter(self) -> tuple:
        timeout = self.component_manager.timeout
        elapsed_time = 0
        start_time = time.time()
        device = self.component_manager._sdp_subarray_dev_name
        while self.sdp_subarray_adapter is None and elapsed_time < timeout:
            try:
                get_adapter = self.adapter_factory.get_or_create_adapter
                self.sdp_subarray_adapter = get_adapter(
                    device,
                    AdapterType.SDPSUBARRAY,
                )
            except ConnectionFailed as cf:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = f"Error in creating adapter for {device}: {cf}"
                    return ResultCode.FAILED, message
            except DevFailed as df:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    message = f"Error in creating adapter for {device}: {df}"
                    return ResultCode.FAILED, message
            except (AttributeError, ValueError, TypeError) as e:
                message = f"Error in creating adapter for {device}: {e}"
                return ResultCode.FAILED, message
        return (ResultCode.OK, "")
