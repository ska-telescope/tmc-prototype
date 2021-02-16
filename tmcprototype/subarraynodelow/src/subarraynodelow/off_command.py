"""
OffCommand class for SubarrayNodeLow
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from tmc.common.tango_client import TangoClient

from . import const


class Off(SKASubarray.OffCommand):
    """
    A class for the SubarrayNodes's Off() command.

    This command invokes Off Command on MCCSSubarray through mccs subarray leaf node. This comamnd
    changes Subaray device state from ON to OFF.

    """

    def do(self):
        """
        Method to invoke Off command.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if the command execution is not successful
        """
        device = self.target
        device.is_release_resources = False
        try:
            mccs_subarray_ln_client = TangoClient(device.mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_OFF, None)
            device.health_state_aggregator.unsubscribe()
            device.obs_state_aggregator.unsubscribe()
            message = "Off command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_INVOKING_OFF_CMD}{dev_failed}"
            self.logger.error(log_msg)
            self._read_activity_message = log_msg
            tango.Except.throw_exception(
                dev_failed[0].desc,
                "Failed to invoke Off command on SubarrayNode.",
                "SubarrayNode.Off()",
                tango.ErrSeverity.ERR,
            )
