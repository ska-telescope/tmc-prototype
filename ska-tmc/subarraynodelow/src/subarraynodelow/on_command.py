"""
OnCommand class for SubarrayNodeLow
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .device_data import DeviceData
from .health_state_aggregator import HealthStateAggregator
from .obs_state_aggregator import ObsStateAggregator


class On(SKASubarray.OnCommand):
    """
    A class for the SubarrayNodeLow's On() command.

    This command invokes On Command on MCCS Subarray through MCCS Subarray Leaf node. This comamnd
    changes Subarray device state from OFF to ON.

    """

    def do(self):
        """
        Method to invoke On command.

        return:
            A tuple containing a return code and a string message indicating status. The message is for
            information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if the command execution is not successful
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        this_server = TangoServerHelper.get_instance()
        try:
            mccs_subarray_ln_fqdn = ""
            property_val = this_server.read_property("MccsSubarrayLNFQDN")
            mccs_subarray_ln_fqdn = mccs_subarray_ln_fqdn.join(property_val)
            mccs_subarray_ln_client = TangoClient(mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_ON, None)
            message = "On command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)
        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_INVOKING_ON_CMD}{dev_failed}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)
            tango.Except.throw_exception(
                dev_failed[0].desc,
                "Failed to invoke On command on SubarrayNode.",
                "SubarrayNode.On()",
                tango.ErrSeverity.ERR,
            )
