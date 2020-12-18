"""
OnCommand class for SubarrayNode
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed, EventType

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from ska.base.control_model import HealthState
from subarraynode.tango_group_client import TangoGroupClient
from subarraynode.tango_client import TangoClient
from subarraynode.device_data import DeviceData


class OnCommand(SKASubarray.OnCommand):
    """
    A class for the SubarrayNode's On() command.
    """

    def do(self):
        """
        This command invokes On Command on CSPSubarray and SDPSubarray through respective leaf nodes. This comamnd
        changes Subaray device state from OFF to ON.

        :return: A tuple containing a return code and a string message indicating status. The message is for
                information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device_data = self.target
        device_data.is_restart_command = False
        device_data.is_release_resources = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        device_data.health_state_aggr.subscribe()
        device_data.obs_state_aggr.subscribe()
        self.set_csp_client()
        self.set_sdp_client()

        message = "On command completed OK"
        self.logger.info(message)
        return (ResultCode.OK, message)

def set_csp_client(self, device_data):
    """
    set up csp devices
    """
    # Create proxy for CSP Subarray Leaf Node
    log_msg = const.STR_SA_PROXY_INIT  + str(device_data.csp_subarray_ln_fqdn)
    csp_subarray_ln_client = TangoClient(device_data.csp_subarray_ln_fqdn)
    self.logger.info(log_msg)
    self.on_leaf_node(csp_subarray_ln_client, "On")

def set_sdp_client(self, device_data):
    """
    set up sdp devices
    """
    # Create proxy for SDP Subarray Leaf Node
    log_msg = const.STR_SA_PROXY_INIT  + str(device_data.sdp_subarray_ln_fqdn)
    sdp_subarray_ln_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
    self.logger.info(log_msg)
    self.on_leaf_node(sdp_subarray_ln_client)

def on_leaf_node(self, tango_client):
    # Invoke ON command on lower level devices
    try:
        tango_client.On()
    except DevFailed as dev_failed:
        log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
        self.logger.exception(log_msg)
        self._read_activity_message = log_msg
        tango.Except.throw_exception(dev_failed[0].desc, const.ERR_INVOKE_ON_CMD_ON_SA,
                                    "SubarrayNode.OnCommand()", tango.ErrSeverity.ERR)

