# TODO : Will get Uncommented after refactoring for command is done.
# """
# Off command class for SDPMasterLeafNode.
# """

# from ska_tango_base.commands import ResultCode

# from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


# class Off(SdpMLNCommand):
#     """
#     A class for SdpMasterLeafNode's Off() command.

#     Off command on SdpMasterLeafNode enables the telescope to perform
#     further operations and observations.
#     It Invokes Off command on Sdp Master device.

#     """

#     def do(self, argin=None):
#         """
#         Method to invoke Off command on Sdp Master.

#         """
#         ret_code, message = self.init_adapter()
#         if ret_code == ResultCode.FAILED:
#             return ret_code, message
#         result = self.call_adapter_method(
#             "Sdp Master", self.sdp_master_adapter, "Off"
#         )
#         return result
