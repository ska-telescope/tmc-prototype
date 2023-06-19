# Will get Uncommented after refactoring for command is done.
# """
# End command class for SDPSubarrayLeafNode.
# """

# from ska_tango_base.commands import ResultCode

# from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
#     AbstractScanEnd,
# )


# class End(AbstractScanEnd):
#     """
#     A class for SdpSubarrayLeafNode's End() command.

#     Invokes End command on SDP Subarray to end the current Scheduling Block.

#     """

#     def do(self, argin=None):
#         """
#         Method to invoke End command on SDP Subarray.

#         :param argin: None

#         return:
#             None

#         """
#         ret_code, message = self.init_adapter()
#         if ret_code == ResultCode.FAILED:
#             return ret_code, message
#         result = self.call_adapter_method(
#             "Sdp Subarray", self.sdp_subarray_adapter, "End"
#         )
#         return result
