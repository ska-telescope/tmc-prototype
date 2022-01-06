# TODO: Refactoring for this command will be done as a part of separate story. Hence commented the code for now.
# """
# Configure class for SDPSubarrayLeafNode.
# """
# # PROTECTED REGION ID(SDPSubarrayLeafNode.additionnal_import) ENABLED START #
# # Tango imports
# import tango

# # Additional import
# from ska.base.commands import BaseCommand
# from ska.base.control_model import ObsState
# from tango import DevFailed, DevState
# from tmc.common.tango_client import TangoClient
# from tmc.common.tango_server_helper import TangoServerHelper

# from . import const
# from .transaction_id import identify_with_id


# class Configure(BaseCommand):
#     """
#     A class for SdpSubarrayLeafNode's Configure() command.

#     Configures the SDP Subarray device by providing the SDP PB
#     configuration needed to execute the receive workflow

#     """

#     def check_allowed(self):
#         """
#         Checks whether this command is allowed to be run in current device state

#         :return: True if this command is allowed to be run in current device state

#         :rtype: boolean

#         :raises: Exception if command execution throws any type of exception

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
#                 f"Configure() is not allowed in current state {self.state_model.op_state}",
#                 "Failed to invoke Configure command on SdpSubarrayLeafNode.",
#                 "sdpsubarrayleafnode.Configure()",
#                 tango.ErrSeverity.ERR,
#             )

#         if self.sdp_sa_ln_client_obj.get_attribute("obsState").value not in [
#             ObsState.IDLE,
#             ObsState.READY,
#         ]:
#             tango.Except.throw_exception(
#                 const.ERR_DEVICE_NOT_READY_OR_IDLE,
#                 const.ERR_CONFIGURE,
#                 "SdpSubarrayLeafNode.ConfigureCommand",
#                 tango.ErrSeverity.ERR,
#             )
#         return True

#     def configure_cmd_ended_cb(self, event):
#         """
#         Callback function immediately executed when the asynchronous invoked command returns.
#         Checks whether the configure command has been successfully invoked on SDP Subarray.

#         :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
#                         callback model for command execution.

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

#     @identify_with_id("configure", "argin")
#     def do(self, argin):
#         """
#         Method to invoke Configure command on SDP Subarray.

#         :param argin: The string in JSON format. The JSON contains following values:

#         Example:
#         {
#           "interface": "https://schema.skao.int/ska-sdp-configure/0.3",
#           "scan_type": "science_A"
#         }

#         return:
#             None

#         raises:
#             ValueError if input argument json string contains invalid value.

#             KeyError if input argument json string contains invalid key.

#             DevFailed if the command execution is not successful
#         """
#         try:
#             log_msg = (
#                 "Input JSON for SDP Subarray Leaf Node Configure command is: "
#                 + argin
#             )
#             self.logger.debug(log_msg)
#             self.sdp_sa_ln_client_obj.send_command_async(
#                 const.CMD_CONFIGURE,
#                 command_data=argin,
#                 callback_method=self.configure_cmd_ended_cb,
#             )
#             self.this_server.write_attr(
#                 "activityMessage", const.STR_CONFIGURE_SUCCESS, False
#             )
#             self.logger.info(const.STR_CONFIGURE_SUCCESS)

#         except DevFailed as dev_failed:
#             log_msg = f"{const.ERR_CONFIGURE}{dev_failed}"
#             self.this_server.write_attr("activityMessage", log_msg, False)
#             self.logger.exception(dev_failed)
#             tango.Except.throw_exception(
#                 const.STR_CONFIG_EXEC,
#                 log_msg,
#                 "SdpSubarrayLeafNode.Configure()",
#                 tango.ErrSeverity.ERR,
#             )
