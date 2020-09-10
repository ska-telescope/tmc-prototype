"""
ObsResetCommand for SubarrayNode.
"""

# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class ObsResetCommand(SKASubarray.ObsResetCommand):
    """
    A class for SubarrayNode's ObsReset() command.
    """

    def do(self):
        """
        This command invokes ObsReset command on CSPSubarrayLeafNode, SDpSubarrayLeafNode and DishLeafNode.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on CSPSubarrayLeafNode, SDpSubarrayLeafNode or
                DishLeafNode.
        """
        device = self.target
        device.is_abort_command = False
        try:
            self.logger.info("ObsReset command invoked on SubarrayNode.")
            # As a part of ObsReset clear the attributes on SubarrayNode
            device._scan_id = ""
            device._sb_id = ""
            device.scan_duration = 0
            device._scan_type = ''
            
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_OBSRESET)
            self.logger.info(const.STR_CMD_OBSRESET_INV_SDP)
            device._csp_subarray_ln_proxy.command_inout(const.CMD_OBSRESET)
            self.logger.info(const.STR_CMD_OBSRESET_INV_CSP)
            device._dish_leaf_node_group.command_inout(const.CMD_OBSRESET)
            self.logger.info(const.STR_CMD_OBSRESET_INV_DISH_GROUP)
        
            device._read_activity_message = const.STR_OBSRESET_SUCCESS
            self.logger.info(const.STR_OBSRESET_SUCCESS)
            device.set_status(const.STR_OBSRESET_SUCCESS)
            device.is_restart_command = True
            return (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_OBSRESET_EXEC,
                                         log_msg,
                                         "SKASubarray.ObsResetCommand",
                                         tango.ErrSeverity.ERR)
