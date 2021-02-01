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
from . import const
from .device_data import DeviceData
from .health_state_aggregator import HealthStateAggregator
from .obs_state_aggregator import ObsStateAggregator


class On(SKASubarray.OnCommand):
    """
    A class for the SubarrayNodeLow's On() command.
    """

    def do(self):
        """
        This command invokes On Command on MCCSSubarray through MCCS Subarray Leaf node. This comamnd
        changes Subarray device state from OFF to ON.

        :return: A tuple containing a return code and a string message indicating status. The message is for
                information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.health_state_aggregator = HealthStateAggregator()
        device_data.obs_state_aggregator = ObsStateAggregator()
        device_data.health_state_aggregator.subscribe()
        device_data.obs_state_aggregator.subscribe()

        try:
            mccs_subarray_ln_client = TangoClient(device_data.mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_ON, None)
            message = "On command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)
        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
            self.logger.error(log_msg)
            self._read_activity_message = log_msg
            tango.Except.throw_exception(
                dev_failed[0].desc,
                "Failed to invoke On command on SubarrayNode.",
                "SubarrayNode.On()",
                tango.ErrSeverity.ERR,
            )
