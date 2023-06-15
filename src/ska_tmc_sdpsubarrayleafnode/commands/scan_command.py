# TODO : Will get Uncommented after refactoring for command is done.
# """
# Scan command class for SDPSubarrayLeafNode.
# """
# import json
# from json import JSONDecodeError

# from ska_tango_base.commands import ResultCode
# from tango import DevFailed

# from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
#     AbstractScanEnd,
# )


# class Scan(AbstractScanEnd):
#     """
#     A class for SdpSubarrayLeafNode's Scan() command.

#     Invoke Scan command to SDP Subarray.
#     """

#     def do(self, argin=None):
#         """
#         Method to invoke Scan command on SDP Subarray. \

#         :param argin: The string in JSON format. The JSON contains following \
#         values: \

#         Example: \
#             { \
#              "interface": "https://schema.skao.int/ska-sdp-scan/0.3", \
#              "scan_id": 1 \
#             } \

#         return: \
#             None
#         """
#         ret_code, message = self.init_adapter()
#         if ret_code == ResultCode.FAILED:
#             return ret_code, message
#         try:
#             json_argument = json.loads(argin)
#         except JSONDecodeError as e:
#             log_msg = (
#                 "Execution of Scan command is failed."
#                 + "Reason: JSON parsing failed with exception: {}".format(e)
#                 + "The command is not executed successfully."
#                 + "The device will continue with normal operation"
#             )
#             self.logger.exception(log_msg)
#             return self.generate_command_result(
#                 ResultCode.FAILED,
#                 (
#                     """Exception occurred while parsing the JSON.
#                     Please check the logs for details."""
#                 ),
#             )

#         log_msg = (
#             f"Invoking Scan command on:{self.sdp_subarray_adapter.dev_name}"
#         )
#         self.logger.info(log_msg)

#         try:
#             # As, SKA logtransaction is not utilised in scan command across
#             # tmc devices.
#             # Hence, Interface URL needs to be updated explicitly for SDP.
#             # pylint: disable=fixme
#             # TODO: Incorporate transaction id implementation for scan
#             # command across TMC.
#             json_argument[
#                 "interface"
#             ] = "https://schema.skao.int/ska-sdp-scan/0.3"
#             log_msg = (
#                 "Input JSON for Scan command for SDP subarray"
#                 "{}: {} ".format(
#                     self.sdp_subarray_adapter.dev_name, json_argument
#                 )
#             )
#             self.logger.debug(log_msg)
#             self.sdp_subarray_adapter.Scan(json.dumps(json_argument))
#         except (AttributeError, ValueError, TypeError, DevFailed) as e:
#             self.logger.exception("Command invocation failed: %s", e)
#             return self.generate_command_result(
#                 ResultCode.FAILED,
#                 "The invocation of the Scan command is failed on Sdp"
#                 + "Subarray Device {}".format(
#                     self.sdp_subarray_adapter.dev_name
#                 )
#                 + "Reason: Error in calling the Scan command on Sdp Subarray."
#                 + "The command has NOT been executed."
#                 + "This device will continue with normal operation."
#                 "",
#             )
#         log_msg = "Scan command successfully invoked on:" + "{}".format(
#             self.sdp_subarray_adapter.dev_name
#         )
#         self.logger.info(log_msg)
#         return (ResultCode.OK, "")
