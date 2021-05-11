import json

# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

import katpoint
from .transaction_id import identify_with_id
from . import const
from .delay_model import DelayManager


class ConfigureCommand(BaseCommand):
    """
    A class for CspSubarrayLeafNode's Configure() command. Configure command is inherited from BaseCommand.

    This command configures a scan. It accepts configuration information in JSON string format and
    invokes Configure command on CSP Subarray.

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
        # device_data = self.target
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Configure() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Configure command on cspsubarrayleafnode.",
                "cspsubarrayleafnode.Configure()",
                tango.ErrSeverity.ERR,
            )
        this_server = TangoServerHelper.get_instance()
        csp_subarray_fqdn = this_server.read_property("CspSubarrayFQDN")[0]
        csp_sa_client = TangoClient(csp_subarray_fqdn)
        if csp_sa_client.get_attribute("obsState").value not in [ObsState.IDLE, ObsState.READY]:
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
        this_server = TangoServerHelper.get_instance()
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)

    @identify_with_id("configure", "argin")
    def do(self, argin):
        """
        Method to invoke Configure command on CSP Subarray.

        :param argin:DevString. The string in JSON format. The JSON contains following values:

        Example:
        {"interface":"https://schema.skatelescope.org/ska-csp-configure/1.0","subarray":{"subarrayName":"science period 23"},"common":{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","subarrayID":"1"},
        "cbf":{"fsp":[{"fspID":1,"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[[0,2],[744,0]],"ChannelOffset":0,"outputLinkMap":[[0,0],[200,1]],"outputHost"
        :[[0,"192.168.1.1"]],"outputPort":[[0,9000,1]]},{"fspID":2,"functionMode":"CORR","frequencySliceID":2,"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[[0,2],[744,0]],"fspChannelOffset":744,
        "outputLinkMap":[[0,4],[200,5]],"outputHost":[[0,"192.168.1.1"]],"outputPort":[[0,9744,1]]}],"vlbi":{},"delayModelSubscriptionPoint":"ska_mid/tm_leaf_node/csp_subarray01/delayModel"},"pss":{},"pst":{},
        "pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}}}

        Note: Enter the json string without spaces as a input.

        return:
            None

        raises:
            DevFailed if the command execution is not successful

            ValueError if input argument json string contains invalid value
        """
        device_data = self.target
        target_Ra = ""
        target_Dec = ""
        this_server = TangoServerHelper.get_instance()
        device_data.fsp_ids_object = []
        try:
            argin_json = json.loads(argin)
            # Used to extract FSP IDs
            device_data.fsp_ids_object = argin_json["cbf"]["fsp"]
            # TODO: Need to check if below lines are required. 
            delay_manager_obj = DelayManager.get_instance()
            delay_manager_obj.update_config_params()
            pointing_params = argin_json["pointing"]
            target_Ra = pointing_params["target"]["RA"]
            target_Dec = pointing_params["target"]["dec"]

            # Create target object
            device_data.target = katpoint.Target(
                f"radec , {target_Ra} , {target_Dec}"
            )
            csp_configuration = argin_json.copy()
            # Keep configuration specific to CSP and delete pointing configuration
            if "pointing" in csp_configuration:
                del csp_configuration["pointing"]
            log_msg = (
                "Input JSON for CSP Subarray Leaf Node Configure command is: " + argin
            )
            self.logger.debug(log_msg)
            csp_subarray_fqdn = ""
            property_val = this_server.read_property("CspSubarrayFQDN")
            csp_subarray_fqdn = csp_subarray_fqdn.join(property_val)
            csp_sub_client_obj = TangoClient(csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(
                const.CMD_CONFIGURE,
                json.dumps(csp_configuration),
                self.configure_cmd_ended_cb,
            )
            this_server.write_attr("activityMessage", const.STR_CONFIGURE_SUCCESS, False)
            self.logger.info(const.STR_CONFIGURE_SUCCESS)

        except ValueError as value_error:
            log_msg = f"{const.ERR_INVALID_JSON_CONFIG}{value_error}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(value_error)
            tango.Except.throw_exception(
                const.ERR_CONFIGURE_INVOKING_CMD,
                log_msg,
                "CspSubarrayLeafNode.ConfigureCommand",
                tango.ErrSeverity.ERR,
            )

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_CONFIGURE_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.ERR_CONFIGURE_INVOKING_CMD,
                log_msg,
                "CspSubarrayLeafNode.ConfigureCommand",
                tango.ErrSeverity.ERR,
            )
