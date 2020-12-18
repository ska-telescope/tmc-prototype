import json
import ast

# Tango imports
import tango
from tango import DevFailed

from ska.base.commands import ResultCode, BaseCommand
from . import const, release
from centralnode.check_receptor_reassignment import CheckReceptorReassignment
from centralnode.input_validator import AssignResourceValidator
from centralnode.tango_client import TangoClient
from centralnode.exceptions import ResourceReassignmentError, ResourceNotPresentError
from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError

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
        Assigns resources to given subarray. It accepts the subarray id, receptor id list and SDP block in JSON
        string format. Upon successful execution, the 'receptorIDList' attribute of the given subarray is populated
        with the given receptors.Also checking for duplicate allocation of resources is done. If already allocated
        it will throw error message regarding the prior existence of resource.

        :param argin: The string in JSON format. The JSON contains following values:

           subarrayID:
               DevShort. Mandatory.

           dish:
               Mandatory JSON object consisting of

               receptorIDList:
                   DevVarStringArray
                   The individual string should contain dish numbers in string format
                   with preceding zeroes upto 3 digits. E.g. 0001, 0002.

           sdp:
               Mandatory JSON object consisting of

               id:
                   DevString
                   The SBI id.
               max_length:
                   DevDouble
                   Maximum length of the SBI in seconds.
               scan_types:
                   array of the blocks each consisting following parameters
                   id:
                       DevString
                       The scan id.
                   coordinate_system:
                       DevString
                   ra:
                       DevString
                   Dec:
                       DevString

               processing_blocks:
                   array of the blocks each consisting following parameters
                   id:
                       DevString
                       The Processing Block id.
                   workflow:
                       type:
                           DevString
                       id:
                           DevString
                       version:
                           DevString
                   parameters:
                       {}

        Example:
            {"subarrayID":1,"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001",
            "max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS","ra":"02:42:40.771"
            ,"dec":"-00:00:47.84","channels":[{"count":744,"start":0,"stride":2,"freq_min":
            0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,"start":2000,
            "stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]},{"id":
            "calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
            "channels":[{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":
            [[0,0],[200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,
            "freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]}],"processing_blocks":[{"id":
            "pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive","version":
            "0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime",
            "id":"test_realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",
            "workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":
            [{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004"
            ,"workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},"parameters":{},"dependencies":
            [{"pb_id":"pb-mvp01-20200325-00003","type":["calibration"]}]}]}}

        Note: From Jive, enter above input string without any space.

        :return: A tuple containing a return code and a string in JSON format on successful assignment
         of given resources. The JSON string contains following values:

            dish:
                Mandatory JSON object consisting of

                receptorIDList_success:
                    DevVarStringArray
                    Contains ids of the receptors which are successfully allocated. Empty on unsuccessful
                    allocation.


            Example:
                {
                "dish": {
                "receptorIDList_success": ["0001", "0002"]
                }
                }

        :rtype: (ResultCode, str)

        :raises: DevFailed when the API fails to allocate resources.

        Note: Enter input without spaces as:{"dish":{"receptorIDList_success":["0001","0002"]}}

        """
        device_data = self.target 
        device_data.receptorIDList = []
        argout = []
        
        
        ## Validate the input JSON string.
        try:
            self.logger.info("Validating input string.")
            input_validator = AssignResourceValidator(device_data.tm_mid_subarray, device_data._dish_leaf_node_devices,
                                                      device_data.dln_prefix, self.logger)
            json_argument = input_validator.loads(argin)

            # Create subarray proxy
            subarrayID = int(json_argument['subarrayID'])
            subarrayFqdn = device_data.subarray_FQDN_dict[subarrayID]
            ## check for duplicate allocation
            self.logger.info("Checking for resource reallocation.")
            check_receptor_reassignment.CheckReceptorReassignment(json_argument["dish"]["receptorIDList"])

            ## Allocate resources to subarray
            # Remove Subarray Id key from input json argument and send the json with
            # receptor Id list and SDP block to TMC Subarray Node
            self.logger.info("Allocating resource to subarray %d", subarrayID)
            input_json_subarray = json_argument.copy()
            del input_json_subarray["subarrayID"]
            input_to_sa = json.dumps(input_json_subarray)
            subarray_client = TangoClient(subarrayFqdn)
         
            resources_allocated_return = subarray_client.send_command(
                const.CMD_ASSIGN_RESOURCES, input_to_sa)

            # Note: resources_allocated_return[1] contains the JSON string containing
            # allocated resources.
            # resources_allocated = resources_allocated_return[1]
            log_msg = "Return value from subarray node: " + str(resources_allocated_return)
            self.logger.info(log_msg)
            resources_allocated = ast.literal_eval(resources_allocated_return[1][0])
            log_msg = "resources_assigned: " + str(resources_allocated)
            self.logger.debug(log_msg)
            # Update self._subarray_allocation variable to update subarray allocation
            # for the related dishes.
            # Also append the allocated dish to out argument.
            for dish in range(0, len(resources_allocated)):
                dish_ID = "dish" + (resources_allocated[dish])
                device_data._subarray_allocation[dish_ID] = "SA" + str(subarrayID)
                receptorIDList.append(resources_allocated[dish])

            # Allocation successful
            device_data._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

            # Prepare output argument
            argout = {
                "dish": {
                    "receptorIDList_success": receptorIDList
                }
            }
            self.logger.debug(argout)
        except (InvalidJSONError, ResourceNotPresentError, SubarrayNotPresentError) as error:
            self.logger.exception("Exception in AssignResource(): %s", str(error))
            device_data._read_activity_message = "Exception in validating input: " + str(error)
            log_msg = const.STR_ASSIGN_RES_EXEC + str(error)
            self.logger.exception(error)
            tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)

        except ResourceReassignmentError as resource_error:
            self.logger.exception("List of the dishes that are already allocated: %s", \
                                  str(resource_error.resources_reallocation))
            device_data._read_activity_message = const.STR_DISH_DUPLICATE + str(resource_error.resources_reallocation)
            log_msg = const.STR_DISH_DUPLICATE + str(resource_error)
            self.logger.exception(resource_error)
            tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)
        except ValueError as ve:
            self.logger.exception("Exception in AssignResources command: %s", str(ve))
            device_data._read_activity_message = "Invalid value in input: " + str(ve)
            log_msg = const.STR_ASSIGN_RES_EXEC + str(ve)
            self.logger.exception(ve)
            tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)
        except DevFailed as dev_failed:
            log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                         "CentralNode.AssignResourcesCommand",
                                         tango.ErrSeverity.ERR)
        message = json.dumps(argout)
        self.logger.info(message)
        return message

        # PROTECTED REGION END #    //  CentralNode.AssignResources

