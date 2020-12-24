"""
AssignResouces class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import ast
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const
from centralnode.device_data import DeviceData
from centralnode.tango_client import TangoClient


class AssignResources(BaseCommand):
    """
    A class for SdpSubarayLeafNode's AssignResources() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception.

        """
        device = self.target
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("AssignResources() is not allowed in current state",
                                    "Failed to invoke AssignResources command on SdpSubarrayLeafNode.",
                                    "sdpsubarrayleafnode.AssignResources()",
                                    tango.ErrSeverity.ERR)

        return True

    def AssignResources_ended(self, event):
        """
        This is the callback method of AssignResources command of the SDP Subarray.
        It checks whether the AssignResources command on SDP subarray is successful.

        :param argin:

            event: response from SDP Subarray for the invoked assign resource command.

        :return: None
        """
        device = self.target
        if event.err:
            log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            device._read_activity_message = log
            self.logger.error(log)
            tango.Except.throw_exception(
                "SDP Subarray returned error while assigning resources",
                str(event.errors),
                event.cmd_name,
                tango.ErrSeverity.ERR
            )
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device._read_activity_message = log
            self.logger.debug(log)

    
    def validate_obs_state(self):
        sdp_subarray_obs_state = self._sdp_subarray_proxy.obsState
        if sdp_subarray_obs_state in [ObsState.EMPTY, ObsState.IDLE]:
            self.logger.info("SDP subarray is in required obstate,Hence resources to SDP can be assign.")
        else:
            self.logger.error("Subarray is not in EMPTY obstate")
            self._read_activity_message = "Error in device obstate."
            raise InvalidObsStateError("SDP subarray is not in EMPTY obstate.")

    @identify_with_id('assign','argin')
    def do(self, argin):
        """
        Assigns resources to given SDP subarray.
        This command is provided as a noop placeholder from SDP subarray.
        Eventually this will likely take a JSON string specifying the resource request.

        :param argin: The string in JSON format. The JSON contains following values:

        SBI ID and maximum length of the SBI:
            Mandatory JSON object consisting of

            SBI ID :
                String

            max_length:
                Float

        Scan types:
            Consist of Scan type id name

            scan_type:
                DevVarStringArray

        Processing blocks:
            Mandatory JSON object consisting of

                processing_blocks:
                    DevVarStringArray

        Example:
            {"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A",
            "coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","channels":[{"count"
            :744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],
            [744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,
            "link_map":[[2000,4],[2200,5]]}]},{"id":"calibration_B","coordinate_system":"ICRS","ra":
            "12:29:06.699","dec":"02:03:08.598","channels":[{"count":744,"start":0,"stride":2,
            "freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,
            "start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]}]
            ,"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":
            "vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":
            {"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},{"id":
            "pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters"
            :{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":
            "pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},"parameters"
            :{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":["calibration"]}]}]}

        Note: Enter input without spaces

        :return: None

        :raises: ValueError if input argument json string contains invalid value.
                    DevFailed if the command execution is not successful.
        """

        device = self.target
        try:
            device.validate_obs_state()
            # Call SDP Subarray Command asynchronously
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_ASSIGN_RESOURCES, argin,
                                                            self.AssignResources_ended)
            # Update the status of command execution status in activity message
            device._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

        except InvalidObsStateError as error:
            self.logger.exception(error)
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_EMPTY_OR_IDLE, "Failed to invoke AssignResources command on ",
                                            "SDP.AssignResources", tango.ErrSeverity.ERR)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON + str(value_error)
            self.logger.exception(log_msg)
            device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                            const.ERR_INVALID_JSON, tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.AssignResourcesCommand()",
                                            tango.ErrSeverity.ERR)
