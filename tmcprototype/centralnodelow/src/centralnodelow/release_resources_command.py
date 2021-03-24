"""
ReleaseResources class for CentralNodeLow.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json

# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class ReleaseResources(BaseCommand):
    """
    A class for CentralNodeLow's ReleaseResources() command.

    Release all the resources assigned to the given Subarray. It accepts the subarray id, release_all flag in JSON string format. When the release_all flag is True, ReleaseAllResources command
    is invoked on the respective SubarrayNode.

    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """

        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(

                f"Command ReleaseResources is not allowed in current state {self.state_model.op_state}.",
                "Failed to invoke ReleaseResources command on CentralNode.",
                "CentralNode.ReleaseResources()",
                tango.ErrSeverity.ERR,
            )
        return True

    def do(self, argin):
        """
        Method to invoke ReleaseResources command on Subarray Node.

        :param argin: The string in JSON format. The JSON contains following values:

            subarray_id:
                DevShort. Mandatory.

            release_all:
                Boolean(True or False). Mandatory. True when all the resources to be released from Subarray.

            Example:
                {"mccs":{"subarray_id":1,"release_all":true}}
            Note: From Jive, enter input as:
                {"mccs":{"subarray_id":1,"release_all":true}} without any space.
        return:
            None

        raises:
            ValueError if input argument json string contains invalid value

            KeyError if input argument json string contains invalid key

            DevFailed if the command execution or command invocation on SubarrayNode is not successful

        """
        device_data = self.target
        try:
            self.this_server = TangoServerHelper.get_instance()
            jsonArgument = json.loads(argin)
            subarray_id = jsonArgument["mccs"]["subarray_id"]
            subarray_fqdn = device_data.subarray_FQDN_dict[subarray_id]
            if jsonArgument["mccs"]["release_all"] == True:
                # Invoke ReleaseAllResources on SubarrayNode
                input_mccs_release = json.dumps(jsonArgument["mccs"])
                subarray_client = TangoClient(subarray_fqdn)
                subarray_client.send_command(const.CMD_RELEASE_RESOURCES)
                # Invoke ReleaseAllResources on MCCS Master Leaf Node
                # Send same input argument to MCCS Master for ReleaseResource Command

                self.mccs_master_ln_fqdn = ""
                property_value = self.this_server.read_property("MCCSMasterLeafNodeFQDN")
                self.mccs_master_ln_fqdn = self.mccs_master_ln_fqdn.join(property_value)

                mccs_mln_client = TangoClient(self.mccs_master_ln_fqdn)
                mccs_mln_client.send_command(
                    const.CMD_RELEASE_MCCS_RESOURCES, input_mccs_release
                )
                log_msg = const.STR_REL_RESOURCES
                self.logger.info(log_msg)

                self.this_server.write_attr("activityMessage", log_msg)
            else:
                self.this_server.write_attr("activityMessage", const.STR_FALSE_TAG)
                self.logger.info(const.STR_FALSE_TAG)

        except ValueError as value_error:
            self.logger.error(const.ERR_INVALID_JSON)
            self.this_server.write_attr("activityMessage", f"{const.ERR_INVALID_JSON}{value_error}")
            log_msg = f"{const.ERR_INVALID_JSON}{value_error}"
            self.logger.exception(value_error)
            tango.Except.throw_exception(
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "CentralNode.ReleaseResourcesCommand",
                tango.ErrSeverity.ERR,
            )

        except KeyError as key_error:
            self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
            self.this_server.write_attr("activityMessage", f"{const.ERR_JSON_KEY_NOT_FOUND}{key_error}")
            log_msg = f"{const.ERR_JSON_KEY_NOT_FOUND}{key_error}"
            self.logger.exception(key_error)
            tango.Except.throw_exception(
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "CentralNode.ReleaseResourcesCommand",
                tango.ErrSeverity.ERR,
            )

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RELEASE_RESOURCES}{dev_failed}"
            self.this_server.write_attr("activityMessage", const.ERR_RELEASE_RESOURCES)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "CentralNode.ReleaseResourcesCommand",
                tango.ErrSeverity.ERR,
            )
