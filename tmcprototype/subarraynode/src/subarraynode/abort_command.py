"""
AbortCommand for SubarrayNode.
"""

from __future__ import print_function
from __future__ import absolute_import

# Tango imports
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class AbortCommand(SKASubarray.AbortCommand):
    """
    A class for SubarrayNode's Abort() command.
    """
    def do(self):
        """
        This command on Subarray Node invokes Abort command on CSP Subarray Leaf Node and SDP
        Subarray Leaf Node, and stops tracking of all the assigned dishes.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs in invoking command on any of the devices like CSPSubarrayLeafNode,
                SDPSubarrayLeafNode or DishLeafNode
        """
        device = self.target
        exception_message = []
        exception_count = 0
        try:
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_ABORT)
            self.logger.info(const.STR_CMD_ABORT_INV_SDP)
            device._csp_subarray_ln_proxy.command_inout(const.CMD_ABORT)
            self.logger.info(const.STR_CMD_ABORT_INV_CSP)
            device._dish_leaf_node_group.command_inout(const.CMD_ABORT)
            device._read_activity_message = const.STR_ABORT_SUCCESS
            self.logger.info(const.STR_ABORT_SUCCESS)
            device.set_status(const.STR_ABORT_SUCCESS)
            device.is_abort_command = True
            return (ResultCode.STARTED, const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                      exception_message,
                                                                                      exception_count,
                                                                                      const.ERR_ABORT_INVOKING_CMD)
        except Exception as except_occurred:
            [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                                                    exception_message, exception_count,
                                                                                    const.ERR_ABORT_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            device.throw_exception(exception_message, const.ERR_ABORT_INVOKING_CMD)
