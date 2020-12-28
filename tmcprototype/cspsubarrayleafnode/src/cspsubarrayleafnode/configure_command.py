import json

# Third Party imports
# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState
from .transaction_id import identify_with_id
from . import const
import katpoint

class ConfigureCommand(BaseCommand):
    """
    A class for CspSubarrayLeafNode's Configure() command.
    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
            current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """
        device = self.target
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Configure() is not allowed in current state",
                                            "Failed to invoke Configure command on cspsubarrayleafnode.",
                                            "cspsubarrayleafnode.Configure()",
                                            tango.ErrSeverity.ERR)

        if device._csp_subarray_proxy.obsState not in [ObsState.IDLE, ObsState.READY]:
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY_OR_IDLE, const.ERR_CONFIGURE_INVOKING_CMD,
                                            "CspSubarrayLeafNode.ConfigureCommand",
                                            tango.ErrSeverity.ERR)
        return True

    def configure_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns.

        :param event: a CmdDoneEvent object. This class is used to pass data
            to the callback method in asynchronous callback model for command
            execution.

        :type: CmdDoneEvent object
            It has the following members:
                - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext

        :return: none
        """
        device = self.target
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device._read_activity_message = log_msg
        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device._read_activity_message = log_msg

    @identify_with_id('configure','argin')
    def do(self, argin):
        """
        This command configures a scan. It accepts configuration information in JSON string format and
        invokes Configure command on CspSubarray.

        :param argin:DevString. The string in JSON format. The JSON contains following values:

        Example:
        {"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","fsp":[{"fspID":1,"functionMode":
        "CORR", "frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":
        [[0,2],[744,0]], "fspChannelOffset":0,"outputLinkMap":[[0,0],[200,1]],"outputHost":[[0,
        "192.168.1.1"]],"outputPort": [[0,9000,1]]},{"fspID":2,"functionMode":"CORR","frequencySliceID":2,
        "integrationTime":1400,"corrBandwidth":0, "channelAveragingMap":[[0,2],[744,0]],
            "fspChannelOffset":744,"outputLinkMap":[[0,4],[200,5]],"outputHost": [[0,"192.168.1.1"]],
            "outputPort":[[0,9744,1]]}],"delayModelSubscriptionPoint":
        "ska_mid/tm_leaf_node/csp_subarray01/delayModel","pointing":{"target":{"system":"ICRS",
        "name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}}}

        Note: Enter the json string without spaces as a input.

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful
                    ValueError if input argument json string contains invalid value
        """
        device = self.target
        target_Ra = ""
        target_Dec = ""
        try:
            argin_json = json.loads(argin)
            # Used to extract FSP IDs
            device.fsp_ids_object = argin_json["fsp"]
            device.update_config_params()
            pointing_params = argin_json["pointing"]
            target_Ra = pointing_params["target"]["RA"]
            target_Dec = pointing_params["target"]["dec"]

            # Create target object
            device.target = katpoint.Target('radec , ' + str(target_Ra) + ", " + str(target_Dec))
            cspConfiguration = argin_json.copy()
            cspConfiguration = argin_json.copy()
            # Keep configuration specific to CSP and delete pointing configuration
            if "pointing" in cspConfiguration:
                del cspConfiguration["pointing"]
            log_msg = "Input JSON for CSP Subarray Leaf Node Configure command is: " + argin
            self.logger.debug(log_msg)
            device._csp_subarray_proxy.command_inout_asynch(const.CMD_CONFIGURE, json.dumps(cspConfiguration),
                                                        self.configure_cmd_ended_cb)
            device._read_activity_message = const.STR_CONFIGURE_SUCCESS
            self.logger.info(const.STR_CONFIGURE_SUCCESS)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON_CONFIG + str(value_error)
            device._read_activity_message = log_msg
            self.logger.exception(value_error)
            tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                            "CspSubarrayLeafNode.ConfigureCommand",
                                            tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_CONFIGURE_INVOKING_CMD + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                            "CspSubarrayLeafNode.ConfigureCommand",
                                            tango.ErrSeverity.ERR)
