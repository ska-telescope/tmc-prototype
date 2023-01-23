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
        adapter_factory=None,
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory or AdapterFactory()

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

        obs_state_val = component_manager.get_device().obs_state

        if obs_state_val not in (
            ObsState.RESOURCING,
            ObsState.CONFIGURING,
            ObsState.SCANNING,
            ObsState.IDLE,
            ObsState.READY,
            ObsState.RESETTING,
        ):
            message = f"""Abort command is not allowed in current observation
            on device {component_manager._sdp_subarray_dev_name}.
            Reason: The current observation state for observation is
            {obs_state_val}.
            The \"Abort\" command has NOT been executed. This device will
            continue with normal operation."""
            raise InvalidObsStateError(message)

        return True

    def do(self, argin=None):
        """
        Method to invoke Abort command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            Exception if error occurs while invoking command on SDP Subarray.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "Abort"
        )
        return result
