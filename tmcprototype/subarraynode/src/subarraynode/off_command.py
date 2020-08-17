"""
OffCommand class for SubarrayNode
"""

from __future__ import print_function
from __future__ import absolute_import

# Tango imports
from tango import DevFailed
# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class OffCommand(SKASubarray.OffCommand):
    """
    A class for the SubarrayNodes's Off() command.
    """
    def do(self):
        """
        This command invokes Off Command on CSPSubarray and SDPSubarray through respective leaf nodes. This comamnd
        changes Subaray device state from ON to OFF.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device = self.target
        exception_message = []
        exception_count = 0
        try:
            device._csp_subarray_ln_proxy.Off()
            device._sdp_subarray_ln_proxy.Off()
            message = "Off command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

        except DevFailed as dev_failed:
            [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                      exception_message,
                                                                                      exception_count,
                                                                                      const.ERR_INVOKING_OFF_CMD)