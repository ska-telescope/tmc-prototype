
"""
 AssignResources class for CentralNodeLow.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
#Tango imports
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base.commands import BaseCommand
from . import const
from .device_data import  DeviceData
from tmc.common.tango_client import TangoClient

class AssignResources(BaseCommand):
    """
    A class for CentralNode's AssignResources() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """

        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command AssignResources is not allowed in current state.",
                                         "Failed to invoke AssignResources command on CentralNode.",
                                         "CentralNode.AssignResources()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self, argin):
        """
        Assigns resources to given subarray. It accepts the subarray id, station ids, station beam id and channels
        in JSON string format.

        :param argin: The string in JSON format. The JSON contains following values:

           subarray_id:
                DevShort. Mandatory.
                Sub-Array to allocate resources to
           station_ids:
                DevArray. Mandatory
                list of stations contributing beams to the data set
           channels:
                DevArray. Mandatory
                list of frequency channels used
           station_beam_ids:
                DevArray. Mandatory
                logical ID of beam

        Example:
            {"mccs":{"subarray_id":1,"station_ids":[1,2],"channels":[[0,8,1,1],[8,8,2,1],[24,16,2,1]],"station_beam_ids":[1]}}

        Note: Enter input without spaces as:{"subarray_id":1,"station_ids":[1,2],"channels":[1,2,3,4,5,6,7,8],"station_beam_ids":[1]}

        :return: None

        :raises: KeyError if input argument json string contains invalid key
                 ValueError if input argument json string contains invalid value
        """
        device_data = self.target
        try:
            json_argument = json.loads(argin)
            subarray_id = int(json_argument['mccs']['subarray_id'])
            subarray_cmd_data = self._create_subarray_cmd_data(json_argument)
            log_msg = f"Assigning resources to subarray :-> {subarray_id}"
            self.logger.info(log_msg)
            subarray_client = self.create_client(subarray_cmd_data, 
                device_data.subarray_FQDN_dict[subarray_id])
            self.invoke_assign_resources(subarray_client, subarray_cmd_data)

            input_mccs_assign = json.dumps(json_argument["mccs"])
            mccs_master_ln_client = self.create_client(device_data.mccs_master_ln_fqdn)
            self.invoke_assign_resources(mccs_master_ln_client, input_mccs_assign)

            device_data._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

        except KeyError as key_error:
            self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
            device_data._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.exception(key_error)
            tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)
        except ValueError as val_error:
            self.logger.exception("Exception in AssignResources command: %s", str(val_error))
            device_data._read_activity_message = "Invalid value in input: " + str(val_error)
            log_msg = const.STR_ASSIGN_RES_EXEC + str(val_error)
            self.logger.exception(val_error)
            tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)

    def _create_subarray_cmd_data(self, json_argument):
        """
                Delete subarray id from json argument and create proxy of subarray corresponding to subarray id
                and call assign_resources_leaf_node method.

                :param json_argument: The string in JSON format.
                        device_data : Object of class device_data

                :return: None
                """
        subarray_id = int(json_argument['mccs']['subarray_id'])
        # Remove subarray_id key from input json argument and send the json to subarray node
        input_json_subarray = json_argument['mccs']
        del input_json_subarray["subarray_id"]
        input_to_subarray = json.dumps(input_json_subarray)
        return input_to_subarray

    # def create_subarray_client(self, cmd_data, subarray_FQDN_dict):
    #     """

    #     :return: None
    #     """
    #     # Allocate resources to subarray
    #     input_to_sa, subarray_id = cmd_data
    #     self.logger.info("Allocating resource to subarray %d", subarray_id)
    #     subarray_fqdn = subarray_FQDN_dict[subarray_id]
    #     subarray_client = TangoClient(subarray_fqdn)
    #     return subarray_client

    def create_client(self, fqdn):
        """
        Creates TangoClient for given FQDN

        :param fqdn: String. FQDN of the Tango device for which client object is to be created.

        return: TangoClient object
        """
        return TangoClient(fqdn)

    # def create_mccs_client(self, mccs_master_ln_fqdn):
    #     """
    #     Create proxy of mccs master leaf node and call method assign_resources_leaf_node.

    #     :param json_argument: The string in JSON format.
    #            device_data : Object of class device_data.

    #     return: None
    #     """
    #     self.logger.info("Invoking AssignResources command on MCCS Master Leaf Node")
    #     mccs_master_ln_client = TangoClient(mccs_master_ln_fqdn)
    #     return mccs_master_ln_client

    def invoke_assign_resources(self, tango_client, input_arg):
        """
        Invokes assign Resources command on leaf node with input argument.

        :param tango_client: client of corresponding leaf node
        :param input_arg: Json string input to invoke command.

        :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode, MCCSMasterLeafNode
        """
        # device_data = DeviceData.get_instance()
        device_data = self.target
        try:
            tango_client.send_command(const.CMD_ASSIGN_RESOURCES, input_arg)
            log_msg = 'Assign resurces command invoked successfully on {}'.format(tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg

        except DevFailed as dev_failed:
            log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)
