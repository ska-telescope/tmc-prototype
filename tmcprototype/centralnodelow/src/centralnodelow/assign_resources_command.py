
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
            {
                "subarray_id": 1,
                "station_ids": [1,2],
                "channels": [1,2,3,4,5,6,7,8],
                "station_beam_ids": [1]
            }

        Note: Enter input without spaces as:{"subarray_id":1,"station_ids":[1,2],"channels":[1,2,3,4,5,6,7,8],"station_beam_ids":[1]}

        :return: None

        :raises: KeyError if input argument json string contains invalid key
                 ValueError if input argument json string contains invalid value
        """
        device_data = self.target
        try:
            json_argument = json.loads(argin)
            self.create_subarray_client(json_argument, device_data)
            self.create_mccs_client(json_argument, device_data)
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


    def create_subarray_client(self, json_argument, device_data):
        """
        Delete subarray id from json argument and create proxy of subarray corresponding to subarray id
        and call assign_resources_leaf_node method.

        :param json_argument: The string in JSON format.
                device_data : Object of class device_data

        :return: None
        """
        subarray_id = int(json_argument['subarray_id'])
        subarray_fqdn = device_data.subarray_FQDN_dict[subarray_id]
        # Remove subarray_id key from input json argument and send the json to subarray node
        input_json_subarray = json_argument.copy()
        del input_json_subarray["subarray_id"]
        input_to_sa = json.dumps(input_json_subarray)
        # Allocate resources to subarray
        self.logger.info("Allocating resource to subarray %d", subarray_id)
        subarray_client = TangoClient(subarray_fqdn)
        self.invoke_assign_resources(subarray_client, input_to_sa)


    def create_mccs_client(self, json_argument, device_data):
        """
        Create proxy of mccs master leaf node and call method assign_resources_leaf_node.

        :param json_argument: The string in JSON format.
               device_data : Object of class device_data.

        return: None
        """
        self.logger.info("Invoking AssignResources command on MCCS Master Leaf Node")
        input_to_mccs = json.dumps(json_argument)
        mccs_master_ln_client = TangoClient(device_data.mccs_master_ln_fqdn)
        self.invoke_assign_resources(mccs_master_ln_client, input_to_mccs)

    def invoke_assign_resources(self, tango_client, input_arg):
        """
        Invokes assign Resources command on leaf node with input argument.

        :param tango_client: client of corresponding leaf node
        :param input_arg: Json string input to invoke command.

        :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode, MCCSMasterLeafNode
        """
        device_data = DeviceData.get_instance()
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

