"""
ReleaseAllResourcesCommand for SubarrayNode
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from subarraynode.tango_group_client import TangoGroupClient
from subarraynode.tango_client import TangoClient
from subarraynode.device_data import DeviceData


class ReleaseAllResourcesCommand(SKASubarray.ReleaseAllResourcesCommand):
    """
    A class for SKASubarray's ReleaseAllResources() command.
    """
    def do(self):
        """
        It checks whether all resources are already released. If yes then it throws error while
        executing command. If not it Releases all the resources from the subarray i.e. Releases
        resources from TMC Subarray Node, CSP Subarray and SDP Subarray. If the command
        execution fails, array of receptors(device names) which are failed to be released from the
        subarray, is returned to Central Node. Upon successful execution, all the resources of a given
        subarray get released and empty array is returned. Selective release is not yet supported.

        :return: A tuple containing a return code and "[]" as a string on successful release all resources.
        Example: "[]" as string on successful release all resources.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_restart_command = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        try:
            assert device_data._dishLnVsHealthEventID != {}, const.RESOURCE_ALREADY_RELEASED
        except AssertionError as assert_err:
            log_message = const.ERR_RELEASE_RES_CMD + str(assert_err)
            self.logger.error(log_message)
            device_data._read_activity_message = log_message
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
                                         const.STR_RELEASE_ALL_RES_EXEC, tango.ErrSeverity.ERR)

        self.logger.info(const.STR_DISH_RELEASE)
        self.remove_receptors_when_release_resources(device_data)
        # device.remove_receptors_from_group()
        self.logger.info(const.STR_CSP_RELEASE)
        self.release_csp_resources(device_data)
        self.logger.info(const.STR_SDP_RELEASE)
        self.release_sdp_resources(device_data)
        device._scan_id = ""
        # For now cleared SB ID in ReleaseAllResources command. When the EndSB command is implemented,
        # It will be moved to that command.
        device._sb_id = ""
        device.is_release_resources = True
        argout = device._dish_leaf_node_group.get_device_list(True)
        log_msg = "Release_all_resources:", argout
        self.logger.debug(log_msg)
        message = str(argout)
        return (ResultCode.STARTED, message)

    def release_csp_resources(self, device_data):
        """
            This function invokes releaseAllResources command on CSP Subarray via CSP Subarray Leaf
            Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        try:
            # device._csp_subarray_ln_proxy.command_inout(const.CMD_RELEASE_ALL_RESOURCES)
            csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
            csp_client.send_command(const.CMD_RELEASE_ALL_RESOURCES)
            self.logger.info(const.STR_RELEASE_ALL_RESOURCES_CSP_SALN)
        except DevFailed as df:
            self.logger.error(const.ERR_CSP_CMD)
            self.logger.debug(df)

    def release_sdp_resources(self, device_data):
        """
            This function invokes releaseAllResources command on SDP Subarray via SDP Subarray Leaf Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        try:
            # device._sdp_subarray_ln_proxy.command_inout(const.CMD_RELEASE_ALL_RESOURCES)
            sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
            sdp_client.send_command(const.CMD_RELEASE_ALL_RESOURCES)
            self.logger.info(const.STR_RELEASE_ALL_RESOURCES_SDP_SALN)

        except DevFailed as df:
            self.logger.error(const.ERR_SDP_CMD)
            self.logger.debug(df)

    def remove_receptors_when_release_resources(self, device_data):
        # Remove the group for receptors.
        # subaraynode_obj = SubarrayNode()
        # device_data.subaraynode_obj.remove_receptors_from_group()