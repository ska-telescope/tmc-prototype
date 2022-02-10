"""
ReleaseResources command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractReleaseResources,
)


class ReleaseResources(AbstractReleaseResources):
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
        super().__init__(target, op_state_model, adapter_factory, logger)

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
                (
                    "Error in calling ReleaseResources on subarray %s",
                    self.sdp_subarray_adapter.dev_name,
                ),
            )
        return (ResultCode.OK, "")
