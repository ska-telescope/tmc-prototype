"""
ReleaseAllResourcesCommand for SubarrayNode
"""

from __future__ import print_function
from __future__ import absolute_import

# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode, ResponseCommand
from ska.base import SKASubarray


class ReleaseAllResourcesCommand(SKASubarray.ReleaseAllResourcesCommand):
    """
    A class for SKASubarray's ReleaseAllResources() command.
    """
    # def __init__(self, target, state_model, logger):
    #     super().__init__(target, state_model, logger)
    #     self.logger = logger
    #     self.target = target
    #     self.state_model = state_model

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

        :raises: Exception if command execution throws any type of exception
                DevFailed if the command execution is not successful
        """
        device = self.target
        device.is_release_resources = False
        try:
            assert device._dishLnVsHealthEventID != {}, const.RESOURCE_ALREADY_RELEASED
        except AssertionError as assert_err:
            log_message = const.ERR_RELEASE_RES_CMD + str(assert_err)
            self.logger.error(log_message)
            device._read_activity_message = log_message
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
                                         const.STR_RELEASE_ALL_RES_EXEC, tango.ErrSeverity.ERR)

        self.logger.info(const.STR_DISH_RELEASE)
        device.remove_receptors_in_group()
        self.logger.info(const.STR_CSP_RELEASE)
        self.release_csp_resources()
        self.logger.info(const.STR_SDP_RELEASE)
        self.release_sdp_resources()
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


    def release_csp_resources(self):
        """
            This function invokes releaseAllResources command on CSP Subarray via CSP Subarray Leaf
            Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        device = self.target
        try:
            device._csp_subarray_ln_proxy.command_inout(const.CMD_RELEASE_ALL_RESOURCES)
            self.logger.info(const.STR_RELEASE_ALL_RESOURCES_CSP_SALN)
        except DevFailed as df:
            self.logger.error(const.ERR_CSP_CMD)
            self.logger.debug(df)

    def release_sdp_resources(self):
        """
            This function invokes releaseAllResources command on SDP Subarray via SDP Subarray Leaf Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        device = self.target
        try:
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_RELEASE_ALL_RESOURCES)
            self.logger.info(const.STR_RELEASE_ALL_RESOURCES_SDP_SALN)

        except DevFailed as df:
            self.logger.error(const.ERR_SDP_CMD)
            self.logger.debug(df)
