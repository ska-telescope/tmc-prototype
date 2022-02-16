"""
ReleaseResources command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.exceptions import InvalidObsStateError

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class ReleaseResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's ReleaseResources() command.

    Releases all the resources of given SDP Subarray Leaf Node.
    It accepts the subarray id, releaseALL flag and receptorIDList in JSON string format.
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

        self.check_op_state("ReleaseResources")
        self.check_unresponsive()
        obs_state_val = component_manager.get_device().obsState
        self.logger.info("sdp_subarray_obs_state value is: %s", obs_state_val)

        if obs_state_val != ObsState.IDLE:
            self.logger.info(
                "sdp_subarray_obs_state value is: %s", obs_state_val
            )
            message = """The invocation of the \"ReleaseResources\" command on this device (subarray {self.sdp_subarray_adapter.dev_name}) is not allowed.
            Reason: The current observation state for observation is {obs_state_val}.
            The \"ReleaseResources\" command has NOT been executed. This device will continue with normal operation."""
            raise InvalidObsStateError(message)
        return True

    def do(self, argin=None):
        """
        Method to invoke ReleaseResources command on SDP Subarray.

        :param argin: None.

        return:
            None
        """

        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.logger.info(
                f"Invoking ReleaseResources command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.ReleaseResources(None)
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the ReleaseResources command is failed on Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the ReleaseResources command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        return (ResultCode.OK, "")
