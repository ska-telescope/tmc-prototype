"""
AssignResouces class for SDPSubarrayLeafNode.
"""
# Tango imports
import tango

# Additional import
from ska.base.commands import BaseCommand
from tango import DevFailed, DevState
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .transaction_id import identify_with_id


class AssignResources(BaseCommand):
    """
    A class for SdpSubarayLeafNode's AssignResources() command.

    Assigns resources to given SDP Subarray.
    This command is provided as a noop placeholder from SDP Subarray.
    Eventually this will likely take a JSON string specifying the resource request.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        Assigns resources to given SDP subarray.
        This command is provided as a noop placeholder from SDP subarray.
        Eventually this will likely take a JSON string specifying the resource request.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception.

        """
        self.this_server = TangoServerHelper.get_instance()
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"AssignResources() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke AssignResources command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        return True

    def assign_resources_ended(self, event):
        """
        This is the callback method of AssignResources command of the SDP Subarray.
        It checks whether the AssignResources command on SDP subarray is successful.

        :param argin:

            event: response from SDP Subarray for the invoked assign resource command.

        return: None
        """
        if event.err:
            log = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.this_server.write_attr("activityMessage", log, False)
            self.logger.error(log)
            tango.Except.throw_exception(
                "SDP Subarray returned error while assigning resources",
                str(event.errors),
                event.cmd_name,
                tango.ErrSeverity.ERR,
            )
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            self.this_server.write_attr("activityMessage", log, False)
            self.logger.debug(log)

    @identify_with_id("assign", "argin")
    def do(self, argin):
        """
        Method to invoke AssignResources command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

            eb_id and maximum length of the SBI:
            Mandatory JSON object consisting of

             eb_id :
                String

            max_length:
                Float

        scan_types:
            Consist of Scan type id name

            scan_type:
                DevVarStringArray

        Processing blocks:
            Mandatory JSON object consisting of

                processing_blocks:
                    DevVarStringArray

        Example:
            {"interface":"https://schema.skao.int/ska-sdp-assignres/0.3",
            "eb_id":"eb-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"scan_type_id":"science_A",
            "reference_frame":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","channels":[{"count":744,"start":0,
            "stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},
            {"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]}
            ,{"scan_type_id":"calibration_B","reference_frame":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
            "channels":[{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],
            [200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,
            "link_map":[[2000,4],[2200,5]]}]}],"processing_blocks":[{"pb_id":"pb-mvp01-20200325-00001","workflow":
            {"kind":"realtime","name":"vis_receive","version":"0.1.0"},"parameters":{}},{"pb_id":
            "pb-mvp01-20200325-00002","workflow":{"kind":"realtime","name":"test_realtime","version":"0.1.0"},
            "parameters":{}},{"pb_id":"pb-mvp01-20200325-00003","workflow":{"kind":"batch","name":"ical",
            "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001",
            "kind":["visibilities"]}]},{"pb_id":"pb-mvp01-20200325-00004","workflow":{"kind":"batch","name":"dpreb",
            "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","kind":
            ["calibration"]}]}]}

        Note: Enter input without spaces

        return:
            None

        raises:
            ValueError if input argument json string contains invalid value.

            DevFailed if the command execution is not successful.
        """
        try:
            # Call SDP Subarray Command asynchronously
            sdp_sa_ln_client_obj = TangoClient(
                self.this_server.read_property("SdpSubarrayFQDN")[0]
            )
            sdp_sa_ln_client_obj.send_command_async(
                const.CMD_ASSIGN_RESOURCES,
                command_data=argin,
                callback_method=self.assign_resources_ended,
            )
            # Update the status of command execution status in activity message
            self.this_server.write_attr(
                "activityMessage", const.STR_ASSIGN_RESOURCES_SUCCESS, False
            )
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

        except ValueError as value_error:
            log_msg = f"{const.ERR_INVALID_JSON}{value_error}"
            self.logger.exception(log_msg)
            self.this_server.write_attr(
                "activityMessage",
                f"{const.ERR_INVALID_JSON}{value_error}",
                False,
            )
            tango.Except.throw_exception(
                const.STR_CMD_FAILED,
                log_msg,
                const.ERR_INVALID_JSON,
                tango.ErrSeverity.ERR,
            )

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ASSGN_RESOURCES}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ASSIGN_RES_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.AssignResources()",
                tango.ErrSeverity.ERR,
            )
