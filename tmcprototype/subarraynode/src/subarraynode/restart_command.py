"""
RestartCommand for SubarrayNode.
"""

from __future__ import print_function
from __future__ import absolute_import

# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class RestartCommand(SKASubarray.RestartCommand):
    """
    A class for SubarrayNode's Restart() command.
    """

    def do(self):
        """
        This command invokes Restart command on CSPSubarrayLeafNode, SDpSubarrayLeafNode and DishLeafNode.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on CSPSubarrayLeafNode, SDpSubarrayLeafNode or
                DishLeafNode.
                Exception if error occurs while executing the command.
        """
        device = self.target
        exception_message = []
        exception_count = 0
        try:
            self.logger.info("Restart command invoked on SubarrayNode.")
            # As a part of Restart clear the attributes on SubarrayNode
            device._scan_id = ""
            device._sb_id = ""
            device.scan_duration = 0
            device._scan_type = ''
            # Remove the group for receptors.
            device.remove_receptors_in_group()
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_RESTART)
            self.logger.info(const.STR_CMD_RESTART_INV_SDP)
            device._csp_subarray_ln_proxy.command_inout(const.CMD_RESTART)
            self.logger.info(const.STR_CMD_RESTART_INV_CSP)
            device._dish_leaf_node_group.command_inout(const.CMD_RESTART)
            self.logger.info(const.STR_CMD_RESTART_INV_DISH_GROUP)
            device._read_activity_message = const.STR_RESTART_SUCCESS
            self.logger.info(const.STR_RESTART_SUCCESS)
            device.set_status(const.STR_RESTART_SUCCESS)
            device.is_restart_command = True
            return (ResultCode.STARTED, const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                      exception_message,
                                                                                      exception_count,
                                                                                      const.ERR_RESTART_INVOKING_CMD)
        except Exception as except_occurred:
            [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                                                    exception_message,
                                                                                    exception_count,
                                                                                    const.ERR_RESTART_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            device.throw_exception(exception_message, const.STR_RESTART_EXEC)
