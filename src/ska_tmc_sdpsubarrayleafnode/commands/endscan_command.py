"""
EndScan command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.exceptions import InvalidObsStateError

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class EndScan(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's EndScan() command.

    It invokes EndScan command on Sdp Subarray.
    This command is allowed when Sdp Subarray is in SCANNING state.
    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory

    def check_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        component_manager = self.target

        self.check_op_state("EndScan")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obsState

        if obs_state_val != ObsState.SCANNING:
            message = f"""EndScan command is not allowed in current observation state on device {component_manager.get_device().dev_name}.
            Reason: The current observation state for observation is {obs_state_val}.
            The \"EndScan\" command has NOT been executed. This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True

    def do(self, argin):
        """
        Method to invoke EndScan command on SDP Subarray.

        """

        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        log_msg = (
            f"Invoking EndScan command on:{self.sdp_subarray_adapter.dev_name}"
        )
        self.logger.info(log_msg)
        try:
            log_msg = (
                "Invoking EndScan command on SDP Subarray %s: ",
                self.sdp_subarray_adapter.dev_name,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.EndScan()

        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the EndScan command is failed on Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the EndScan command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        log_msg = f"EndScan command successfully invoked on:{self.sdp_subarray_adapter.dev_name}"
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
