# TODO : Will get Uncommented after refactoring for command is done.
# """
# Restart command class for SDPSubarrayLeafNode.
# """

# from ska_tango_base.commands import ResultCode

# from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
#     AbstractRestartObsReset,
# )


# class Restart(AbstractRestartObsReset):
#     """
#     A class for SdpSubarrayLeafNode's Restart() command.

#     Command to reset the SDP Subarray and bring it to its RESTARTING state.
#     """

#     def do(self, argin=None):
#         """
#         Method to invoke Restart command on SDP Subarray.

#         :param argin: None

#         return:
#             None
#         """

#         ret_code, message = self.init_adapter()
#         if ret_code == ResultCode.FAILED:
#             return ret_code, message
#         result = self.call_adapter_method(
#             "Sdp Subarray", self.sdp_subarray_adapter, "Restart"
#         )
#         return result
