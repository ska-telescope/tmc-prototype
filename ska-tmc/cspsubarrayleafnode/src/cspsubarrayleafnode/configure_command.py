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
        {"interface":"https://schema.skao.int/ska-csp-configure/1.0","subarray":
        {"subarray_name":"science period 23"},"common":{"config_id":
        "sbi-mvp01-20200325-00001-science_A","frequency_band":"1","band_5_tuning"
        :[5.85,7.25],"subarray_id":"1"},"cbf":{"frequency_band_offset_stream_1":0,
        "frequency_band_offset_stream_2":0,"doppler_phase_corr_subscription_point":
        "ska_mid/tm_leaf_node/csp_subarray_01/dopplerPhaseCorrection",
        "jones_matrix_subscription_point":"ska_mid/tm_leaf_node/csp_subarray_01/jonesMatrix",
        "delay_model_subscription_point":"ska_mid/tm_leaf_node/csp_subarray_01/delayModel",
        "timing_beam_weights_subscription_point":"ska_mid/tm_leaf_node/csp_subarray_01/beamWeights",
        "rfi_flagging_mask":{},"search_window":[{"search_window_id":1,
        "search_window_tuning":6000000000,"tdc_enable":true,"tdc_num_bits":8,"tdc_period_before_epoch":5,
        "tdc_period_after_epoch":25,"tdc_destination_address":[{"receptor_id":4,"tdc_destination_address":
        ["foo","bar","8080"]},{"receptor_id":1,"tdc_destination_address":["fizz","buzz","80"]}]},
        {"search_window_id":2,"search_window_tuning":7000000000,"tdc_enable":false}],"fsp":
        [{"fsp_id":1,"function_mode":"CORR","receptor_ids":[4],"frequency_slice_id":1,
        "zoom_factor":1,"zoom_window_tuning":4700000,"integration_factor":1,"channel_offset":14880,
        "channel_averaging_map":[[0,8],[1,8],[2,8],[3,8],[4,8],[5,8],[6,8],[7,8],[8,8],[9,8],[10,8],
        [11,8],[12,8],[13,8],[14,8],[15,8],[16,8],[17,8],[18,8],[19,8]],"output_link_map":[[0,4],
        [1,8],[2,12],[3,16],[4,20],[5,24],[6,28],[7,32],[8,36],[9,40],[10,44],[11,48],[12,52],
        [13,56],[14,60],[15,64],[16,68],[17,72],[18,76],[19,80]],"output_host":[[0,"192.168.0.1"],
        [8184,"192.168.0.2"]],"output_mac":[[0,"06-00-00-00-00-01"]],"output_port":[[0,9000,1],
        [8184,9000,1]]},{"fsp_id":3,"function_mode":"PSS-BF","search_window_id":2,"search_beam":
        [{"search_beam_id":300,"receptor_ids":[3],"enable_output":true,"averagingInterval":4,
        "search_beam_destination_address":"10.1.1.1"},{"search_beam_id":400,"receptor_ids":[1],
        "enable_output":true,"averagingInterval":2,"search_beam_destination_address":"10.1.2.1"}]},
        {"fsp_id":2,"function_mode":"PST-BF","timing_beam":[{"timing_beam_id":10,"receptor_ids":[2],
        "enable_output":true,"timing_beam_destination_address":"10.1.1.1"}]}],"vlbi":{}},"pss":{},
        "pst":{},"pointing":{"target":{"system":"ICRS","target_name":"Polaris Australis",
        "ra":"21:08:47.92","dec":"-88:57:22.9"}}}

        Note: Enter the json string without spaces as a input.

        return:
            None

        raises:
            DevFailed if the command execution is not successful

            ValueError if input argument json string contains invalid value
        """
        device_data = self.target
        target_ra = ""
        target_dec = ""
        this_server = TangoServerHelper.get_instance()
        device_data.fsp_ids_object = []
        try:
            argin_json = json.loads(argin)
            # Used to extract FSP IDs
            device_data.fsp_ids_object = argin_json["cbf"]["fsp"]
            delay_manager_obj = DelayManager.get_instance()
            delay_manager_obj.update_config_params()
            pointing_params = argin_json["pointing"]
            target_Ra = pointing_params["target"]["ra"]
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
