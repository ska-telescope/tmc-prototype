# """
# Scan class for SDPSubarrayLeafNode.
# """
# import json

# # PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# # Tango imports
# import tango

# # Additional import
# from ska.base.commands import BaseCommand
# from ska.base.control_model import ObsState
# from tango import DevFailed, DevState
# from tmc.common.tango_client import TangoClient
# from tmc.common.tango_server_helper import TangoServerHelper

# from . import const


# class Scan(BaseCommand):
#     """
#     A class for SdpSubarrayLeafNode's Scan() command.

#     Invoke Scan command to SDP Subarray.
#     """

#     def check_allowed(self):
#         """
#         Checks whether this command is allowed to be run in current device state.

#         :return: True if this command is allowed to be run in current device state.

#         :rtype: boolean

#         :raises: Exception if command execution throws any type of exception.

#         """
#         self.this_server = TangoServerHelper.get_instance()
#         sdp_subarray_fqdn = self.this_server.read_property("SdpSubarrayFQDN")[
#             0
#         ]
#         self.sdp_sa_ln_client_obj = TangoClient(sdp_subarray_fqdn)

#         if self.state_model.op_state in [
#             DevState.FAULT,
#             DevState.UNKNOWN,
#             DevState.DISABLE,
#         ]:
#             tango.Except.throw_exception(
#                 f"Scan() is not allowed in current state {self.state_model.op_state}",
#                 "Failed to invoke Scan command on SdpSubarrayLeafNode.",
#                 "sdpsubarrayleafnode.Scan()",
#                 tango.ErrSeverity.ERR,
#             )

#         if (
#             self.sdp_sa_ln_client_obj.get_attribute("obsState").value
#             != ObsState.READY
#         ):
#             tango.Except.throw_exception(
#                 const.ERR_DEVICE_NOT_READY,
#                 const.STR_SCAN_EXEC,
#                 "SdpSubarrayLeafNode.StartScanCommand",
#                 tango.ErrSeverity.ERR,
#             )
#         return True

#     def scan_cmd_ended_cb(self, event):
#         """
#         Callback function immediately executed when the asynchronous invoked command returns.
#         Checks whether the scan command has been successfully invoked on SDP Subarray.

#         :param event: A CmdDoneEvent object.
#         This class is used to pass data to the callback method in asynchronous callback model
#             for command execution.

#         :type: CmdDoneEvent object

#             It has the following members:
#                 - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
#                 - cmd_name   : (str) The command name
#                 - argout_raw : (DeviceData) The command argout
#                 - argout     : The command argout
#                 - err        : (bool) A boolean flag set to true if the command failed. False otherwise
#                 - errors     : (sequence<DevError>) The error stack
#                 - ext

#         :return: none
#         """
#         if event.err:
#             log = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
#             self.this_server.write_attr("activityMessage", log, False)
#             self.logger.error(log)
#         else:
#             log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
#             self.this_server.write_attr("activityMessage", log, False)
#             self.logger.info(log)

#     def do(self, argin):
#         """
#         Method to invoke Scan command on SDP Subarray.

#         :param argin: The string in JSON format. The JSON contains following values:

#         Example:
#         {
#              "interface": "https://schema.skao.int/ska-sdp-scan/0.3",
#              "scan_id": 1
#         }

#         Note: Enter input as without spaces: {"interface":"https://schema.skao.int/ska-sdp-scan/0.3","scan_id":1}

#         return:
#             None

#         raises:
#             DevFailed if the command execution is not successful.
#         """
#         try:
#             log_msg = (
#                 "Input JSON for SDP Subarray Leaf Node Scan command is: "
#                 + argin
#             )
#             self.logger.debug(log_msg)
#             # As, SKA logtransaction is not utilised in scan command across tmc devices.
#             # Hence, Interface URL needs to be updated explicitly for SDP.
#             # TODO: Incorporate transaction id implementation for scan command across TMC.
#             input_json = json.loads(argin)
#             input_json[
#                 "interface"
#             ] = "https://schema.skao.int/ska-sdp-scan/0.3"
#             updated_argin = json.dumps(input_json)
#             self.sdp_sa_ln_client_obj.send_command_async(
#                 const.CMD_SCAN,
#                 command_data=updated_argin,
#                 callback_method=self.scan_cmd_ended_cb,
#             )
#             self.this_server.write_attr(
#                 "activityMessage", const.STR_SCAN_SUCCESS, False
#             )
#             self.logger.info(const.STR_SCAN_SUCCESS)

#         except DevFailed as dev_failed:
#             log_msg = f"{const.ERR_SCAN}{dev_failed}"
#             self.this_server.write_attr("activityMessage", log_msg, False)
#             self.logger.exception(dev_failed)
#             tango.Except.throw_exception(
#                 const.STR_SCAN_EXEC,
#                 log_msg,
#                 "SdpSubarrayLeafNode.Scan()",
#                 tango.ErrSeverity.ERR,
#             )
