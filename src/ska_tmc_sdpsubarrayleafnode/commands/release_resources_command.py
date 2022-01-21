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

    def do_mid(self, argin=None):
        """
        Method to invoke ReleaseResources command on SDP Subarray.

        :param argin: None.

        return:
            None
        """

        res_code, message = self.init_adapters_mid()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.logger.info(
                f"Invoking ReleaseResources command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.ReleaseResources(None)
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling ReleaseResources on subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
