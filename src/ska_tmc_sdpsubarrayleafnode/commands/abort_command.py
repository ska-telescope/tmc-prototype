"""
Abort command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.exceptions import InvalidObsStateError

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Abort(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's Abort() command.

    Command to abort the SDP Subarray and bring it to its ABORTED state.
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

        self.check_op_state("Abort")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obsState

        if obs_state_val not in (
            ObsState.CONFIGURING,
            ObsState.SCANNING,
            ObsState.IDLE,
            ObsState.READY,
            ObsState.RESETTING,
        ):
            message = f"""Abort command is not allowed in current observation on device {component_manager.get_device().dev_name}.
            Reason: The current observation state for observation is {obs_state_val}.
            The \"Abort\" command has NOT been executed. This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True

    def do_mid(self, argin=None):
        """
        Method to invoke Abort command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            Exception if error occurs while invoking command on SDP Subarray.

        """
        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        log_msg = (
            f"Invoking Abort command on:{self.sdp_subarray_adapter.dev_name}"
        )
        self.logger.info(log_msg)
        try:
            log_msg = (
                "Invoking Abort command on SDP Subarray %s: ",
                self.sdp_subarray_adapter.dev_name,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Abort()
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Abort command is failed on Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the Abort command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )

        log_msg = f"Abort command successfully invoked on:{self.sdp_subarray_adapter.dev_name}"
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
