"""
ReleaseResources class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import ast

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const
from centralnode.device_data import DeviceData
from centralnode.tango_client import TangoClient

class ReleaseResources(BaseCommand):
    """
    A class for CentralNode's ReleaseResources() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """

        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE, ]:
            tango.Except.throw_exception("Command ReleaseResources is not allowed in current state.",
                                         "Failed to invoke ReleaseResources command on CentralNode.",
                                         "CentralNode.ReleaseResources()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self, argin):
        """
        Release all the resources assigned to the given Subarray. It accepts the subarray id, releaseALL flag and
        receptorIDList in JSON string format. When the releaseALL flag is True, ReleaseAllResources command
        is invoked on the respective SubarrayNode. In this case, the receptorIDList tag is empty as all
        the resources of the Subarray are to be released.
        When releaseALL is False, ReleaseResources will be invoked on the SubarrayNode and the resources provided
        in receptorIDList tag, are to be released from the Subarray. The selective release of the resources when
        releaseALL Flag is False is not yet supported.

        :param argin: The string in JSON format. The JSON contains following values:

            subarrayID:
                DevShort. Mandatory.

            releaseALL:
                Boolean(True or False). Mandatory. True when all the resources to be released from Subarray.

            receptorIDList:
                DevVarStringArray. Empty when releaseALL tag is True.

            Example:
                {
                    "subarrayID": 1,
                    "releaseALL": true,
                    "receptorIDList": []
                }

            Note: From Jive, enter input as:
                {"subarrayID":1,"releaseALL":true,"receptorIDList":[]} without any space.

        :return: A tuple containing a return code and a string in josn format on successful release
         of all the resources. The JSON string contains following values:

            releaseALL:
                Boolean(True or False). If True, all the resources are successfully released from the
                Subarray.

            receptorIDList:
                DevVarStringArray. If releaseALL is True, receptorIDList is empty. Else list returns
                resources (device names) that are noe released from the subarray.

            Example:
                argout =
                {
                    "ReleaseAll" : True,
                    "receptorIDList" : []
                }

         :rtype: (ResultCode, str)

         :raises: ValueError if input argument json string contains invalid value
                KeyError if input argument json string contains invalid key
                DevFailed if the command execution or command invocation on SubarrayNode is not successful

        """
        device_data = self.target
        self.logger.info(type(self.target))

        try:
            release_success = False
            jsonArgument = json.loads(argin)
            subarrayID = jsonArgument['subarrayID']
            subarray_fqdn = device_data.subarray_FQDN_dict[subarrayID]
            subarray_client = TangoClient(subarray_fqdn)
            subarray_name = "SA" + str(subarrayID)
            if jsonArgument['releaseALL'] == True:
                # Invoke "ReleaseAllResources" on SubarrayNode
                return_val = subarray_client.send_command(const.CMD_RELEASE_RESOURCES)
                res_not_released = ast.literal_eval(return_val[1][0])
                log_msg = const.STR_REL_RESOURCES
                self.logger.info(log_msg)
                device_data._read_activity_message = log_msg
                if not res_not_released:
                    release_success = True
                    for Dish_ID, Dish_Status in device_data._subarray_allocation.items():
                        if Dish_Status == subarray_name:
                            device_data._subarray_allocation[Dish_ID] = "NOT_ALLOCATED"
                    argout = {
                        "ReleaseAll": release_success,
                        "receptorIDList": res_not_released
                    }
                    message = json.dumps(argout)
                    self.logger.info(message)
                    return message
                else:
                    log_msg = const.STR_LIST_RES_NOT_REL + str(res_not_released)
                    device_data._read_activity_message = log_msg
                    self.logger.info(log_msg)
                    # release_success = False
            else:
                device_data._read_activity_message = const.STR_FALSE_TAG
                self.logger.info(const.STR_FALSE_TAG)

        except ValueError as value_error:
            self.logger.error(const.ERR_INVALID_JSON)
            device_data._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
            log_msg = const.ERR_INVALID_JSON + str(value_error)
            self.logger.exception(value_error)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                         "CentralNode.ReleaseResourcesCommand",
                                         tango.ErrSeverity.ERR)

        except KeyError as key_error:
            self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
            device_data._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.exception(key_error)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                         "CentralNode.ReleaseResourcesCommand",
                                         tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RELEASE_RESOURCES + str(dev_failed)
            device_data._read_activity_message = const.ERR_RELEASE_RESOURCES
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                         "CentralNode.ReleaseResourcesCommand",
                                         tango.ErrSeverity.ERR)


