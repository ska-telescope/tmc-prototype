"""
ReleaseResources class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(SDPSubarrayLeafNode.additionnal_import) ENABLED START #
import json

# Tango imports
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractReleaseResources,
)
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid


class ReleaseAllResources(AbstractReleaseResources):
    """
    A class for SdpSubarayLeafNode's ReleaseAllResources() command.

    Releases all the resources of given SDP Subarray Leaf Node.
    It accepts the subarray id, releaseALL flag and receptorIDList in JSON string format.
    """

    def __init__(
        self,
        target,
        pop_state_model,
        adapter_factory=AdapterFactory(),
        timeout_sdp=3000,
        step_sleep=0.1,
        *args,
        logger=None,
        **kwargs,
    ):
        super().__init__(
            target, pop_state_model, adapter_factory, args, logger, kwargs
        )
        self._timeout_sdp = timeout_sdp
        self._step_sleep = step_sleep

    def do_mid(self, argin=None):
        """
        Method to invoke ReleaseResources command on SDP Subarray.

        :param argin: None.

        return:
            None

        raises:
            DevFailed if the command execution is not successful.
        """

        res_code, message = self.init_adapters()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.sdp_subarray_adapter.ReleaseResources(argin=None)
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