"""
 AssignResources class for CentralNodeLow.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import time
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class AssignResources(BaseCommand):
    """
    A class for CentralNode's AssignResources() command.

    Assigns resources to given subarray. It accepts the subarray id, mccs string which contains subarray_beam_ids, station id and channels blocks
    in JSON string format.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """

        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Command AssignResources is not allowed in current state {self.state_model.op_state}.",
                "Failed to invoke AssignResources command on CentralNode.",
                "CentralNode.AssignResources()",
                tango.ErrSeverity.ERR,
            )
        return True

    def do(self, argin):
        """
        Method to invoke AssignResources command on Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

           interface:
                DevString. Mandatory.
                Version of schema to allocate assign resources.

           subarray_id:
                DevShort. Mandatory.
                Sub-Array to allocate resources to

           mccs:
                subarray_beam_ids:
                    DevArray. Mandatory
                    logical ID of beam
                station_ids:
                    DevArray. Mandatory
                    list of stations contributing beams to the data set
                channel_blocks:
                    DevArray. Mandatory
                    list of channels used


        Example:
            {"interface":"https://schema.skatelescope.org/ska-low-tmc-assignresources/1.0","subarray_id":1,"mccs":{"subarray_beam_ids":[1],"station_ids":[[1,2]],"channel_blocks":[3]},"sdp":{}}

        Note: Enter input without spaces as: {"interface":"https://schema.skatelescope.org/ska-low-tmc-assignresources/1.0","subarray_id":1,"mccs":{"subarray_beam_ids":[1],"station_ids":[[1,2]],"channel_blocks":[3]},"sdp":{}}

        return:
            None

        raises:
            KeyError if input argument json string contains invalid key

            ValueError if input argument json string contains invalid value

            AssertionError if  Mccs On command is not completed.

        """
        device_data = self.target
        try:
            self.this_server = TangoServerHelper.get_instance()
            # Check if Mccs On command is completed
            cmd_res = json.loads(device_data.cmd_res_evt_val)
            log_msg = "commandresult attribute value in StandByTelescope command", cmd_res
            self.logger.debug(log_msg)

            if cmd_res["result_code"] != 0:
                retry = 0
                while retry < 3:
                    if cmd_res["result_code"] == 0:
                        break
                    retry += 1
                    time.sleep(0.1)

            assert cmd_res["result_code"] == 0, "Startup command completed OK"
            json_argument = json.loads(argin)
            subarray_id = int(json_argument["subarray_id"])
            subarray_cmd_data = self._create_subarray_cmd_data(json_argument)
            log_msg = f"Assigning resources to subarray :-> {subarray_id}"
            self.logger.info(log_msg)
            subarray_client = self.create_client(
                device_data.subarray_FQDN_dict[subarray_id]
            )
            self.invoke_assign_resources(subarray_client, subarray_cmd_data)

            mccs_string = json.loads(argin)
            input_mccs_master = self._create_mccs_cmd_data(mccs_string)
            self.mccs_master_ln_fqdn = ""
            property_value = self.this_server.read_property("MCCSMasterLeafNodeFQDN")
            self.mccs_master_ln_fqdn = self.mccs_master_ln_fqdn.join(property_value)

            mccs_master_ln_client = self.create_client(self.mccs_master_ln_fqdn)
            self.invoke_assign_resources(mccs_master_ln_client, input_mccs_master)

            self.this_server.write_attr("activityMessage", const.STR_ASSIGN_RESOURCES_SUCCESS, False)
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)


        except KeyError as key_error:
            self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
            self.this_server.write_attr("activityMessage", f"{const.ERR_JSON_KEY_NOT_FOUND}{key_error}", False)
            log_msg = f"{const.ERR_JSON_KEY_NOT_FOUND}{key_error}"
            self.logger.exception(key_error)
            tango.Except.throw_exception(
                const.STR_RESOURCE_ALLOCATION_FAILED,
                log_msg,
                "CentralNode.AssignResourcesCommand",
                tango.ErrSeverity.ERR,
            )
        except ValueError as val_error:
            self.logger.exception(
                "Exception in AssignResources command: %s", str(val_error)
            )
            self.this_server.write_attr("activityMessage", f"Invalid value in input: {val_error}", False)
            log_msg = f"{const.STR_ASSIGN_RES_EXEC}{val_error}"
            self.logger.exception(val_error)
            tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)
        except AssertionError:
            log_msg = "Exception in AssignResources command: " + const.ERR_STARTUP_CMD_INCOMPLETE
            self.logger.exception(log_msg)
            log_msg = const.STR_ASSIGN_RES_EXEC + const.ERR_STARTUP_CMD_INCOMPLETE
            self.logger.exception(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)
            tango.Except.throw_exception(const.ERR_STARTUP_CMD_INCOMPLETE, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)

        message = const.STR_RETURN_MSG_ASSIGN_RESOURCES_SUCCESS
        self.logger.info(message)
        return message

    def _create_mccs_cmd_data(self, json_argument):
        """
        Remove 'sdp' and 'mccs' key from input JSON argument and forward the updated JSON to mccs master leaf node.

        :param json_argument: The string in JSON format.

        :return: The string in JSON format.
        """
        mccs_value = json_argument["mccs"]
        json_argument["interface"] = "https://schema.skatelescope.org/ska-low-mccs-assignresources/1.0"
        del json_argument["sdp"]
        del json_argument["mccs"]
        json_argument.update(mccs_value)
        input_to_mccs= json.dumps(json_argument)
        return input_to_mccs

    def _create_subarray_cmd_data(self, json_argument):
        """
        Remove 'subarray id', 'sdp' from json argument and forward the updated JSON to Subarray node.

        :param json_argument: The string in JSON format.

        :return: The string in JSON format.
        """
        # Remove subarray_id key from input json argument and send the json to subarray node
        del json_argument["subarray_id"]
        del json_argument["sdp"]
        input_to_subarray = json.dumps(json_argument)
        return input_to_subarray

    def create_client(self, fqdn):
        """
        Creates TangoClient for given FQDN

        :param fqdn: String. FQDN of the Tango device for which client object is to be created.

        return: TangoClient object
        """
        return TangoClient(fqdn)

    def invoke_assign_resources(self, tango_client, input_arg):
        """
        Invokes assign Resources command on leaf node with input argument.

        :param tango_client: client of corresponding leaf node
        :param input_arg: Json string input to invoke command.

        :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode, MCCSMasterLeafNode
        """
        try:
            tango_client.send_command(const.CMD_ASSIGN_RESOURCES, input_arg)
            log_msg = "Assign resurces command invoked successfully on {}".format(
                tango_client.get_device_fqdn
            )
            self.logger.debug(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ASSGN_RESOURCES}{dev_failed}"
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_CMD_FAILED,
                log_msg,
                "CentralNode.AssignResourcesCommand",
                tango.ErrSeverity.ERR,
            )
