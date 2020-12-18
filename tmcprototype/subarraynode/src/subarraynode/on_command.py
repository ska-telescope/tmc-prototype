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
        self.set_client_for_csp_devices()
        self.set_client_for_sdp_devices()
        self.subscribe_attributes_from_csp()
        # How to set Status using TangoServer API?
        device_data.set_status(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
        self.logger.info(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
        
        self.subscribe_attributes_from_sdp()
        device_data.set_status(const.STR_SDP_SA_LEAF_INIT_SUCCESS)
        
        self.send_on_command(device_data)

        message = "On command completed OK"
        self.logger.info(message)
        return (ResultCode.OK, message)

def send_on_command(self, device_data):
    # Invoke ON command on lower level devices
    try:
        device_data.csp_subarray_ln_proxy.On()
        device_data.sdp_subarray_ln_proxy.On()
    except DevFailed as dev_failed:
        log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
        self.logger.exception(log_msg)
        self._read_activity_message = log_msg
        tango.Except.throw_exception(dev_failed[0].desc, const.ERR_INVOKE_ON_CMD_ON_SA,
                                    "SubarrayNode.OnCommand()", tango.ErrSeverity.ERR)

def set_client_csp_devices(self, device_data):
    """
    set up csp devices
    """
    try:
        # Create proxy for CSP Subarray Leaf Node
        log_msg = const.STR_SA_PROXY_INIT  + str(device_data.csp_subarray_ln_fqdn)
        self.csp_subarray_ln_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        self.logger.info(log_msg)
        # Create proxy for CSP Subarray
        self.csp_sa_client = TangoClient(device_data.csp_sa_proxy)

    except DevFailed as dev_failed:
        log_msg = const.ERR_CSP_PROXY_CREATE
        self.logger.debug(log_msg)
        tango.Except.throw_exception(dev_failed[0].desc, const.ERR_CREATE_PROXY,
                                        "SubarrayNode.OnCommand()", tango.ErrSeverity.ERR)

def set_client_for_sdp_devices(self, device_data):
    """
    set up sdp devices
    """
    try:
        # Create proxy for SDP Subarray Leaf Node
        log_msg = const.STR_SA_PROXY_INIT  + str(device_data.sdp_subarray_ln_fqdn)
        self.sdp_subarray_ln_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        self.logger.info(log_msg)            
        self.sdp_sa_client = TangoClient(device_data.sdp_sa_proxy)

    except DevFailed as dev_failed:
        log_msg = const.ERR_SDP_PROXY_CREATE
        self.logger.debug(log_msg)
        tango.Except.throw_exception(dev_failed[0].desc, const.ERR_CREATE_PROXY,
                                        "SubarrayNode.OnCommand()", tango.ErrSeverity.ERR)

def subscribe_attributes_from_csp(self, device_data):
    try:
        # TODO: dev_name() where to keep this API?
        device_data.health_state_aggr.subarray_ln_health_state_map[device_data.csp_subarray_ln_proxy.dev_name()] = (
            HealthState.UNKNOWN)
        # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
        csp_health_state_event_id = self.csp_subarray_ln_client.subscribe_attribute(const.EVT_CSPSA_HEALTH, device_data.health_state_aggr.health_state_cb)
        device_data.csp_sdp_ln_health_event_id[device_data.csp_subarray_ln_proxy] = csp_health_state_event_id
        log_msg = const.STR_CSP_LN_VS_HEALTH_EVT_ID + str(device_data.csp_sdp_ln_health_event_id)
        self.logger.debug(log_msg)

        # Subscribe cspSubarrayObsState (forwarded attribute) of CspSubarray
        csp_obs_state_event_id = self.csp_subarray_ln_client.subscribe_attribute(const.EVT_CSPSA_OBS_STATE, device_data.obs_state_aggr.observation_state_cb)
        device_data.csp_sdp_ln_obs_state_event_id[device_data.csp_subarray_ln_proxy] = csp_obs_state_event_id
        log_msg = const.STR_CSP_LN_VS_HEALTH_EVT_ID + str(device_data.csp_sdp_ln_obs_state_event_id)
        self.logger.debug(log_msg)

    except DevFailed as dev_failed:
        log_msg = const.ERR_SUBS_CSP_SA_LEAF_ATTR + str(dev_failed)
        device_data._read_activity_message = log_msg
        device_data.set_status(const.ERR_SUBS_CSP_SA_LEAF_ATTR)
        self.logger.exception(dev_failed)
        tango.Except.throw_exception(const.ERR_SUBS_CSP_SA_LEAF_ATTR,
                                        log_msg,
                                        "SubarrayNode.OnCommand()",
                                        tango.ErrSeverity.ERR)

def subscribe_attributes_from_sdp(self, device_data):
    try:
        device_data.health_state_aggr.subarray_ln_health_state_map[device_data.sdp_subarray_ln_proxy.dev_name()] = (
            HealthState.UNKNOWN)
        # Subscribe sdpSubarrayHealthState (forwarded attribute) of SdpSubarray
        sdp_health_state_event_id = self.sdp_subarray_ln_client.subscribe_attribute(const.EVT_SDPSA_HEALTH, device_data.health_state_aggr.health_state_cb)
        
        
        device_data.csp_sdp_ln_health_event_id[device_data.sdp_subarray_ln_proxy] = sdp_health_state_event_id
        log_msg = const.STR_SDP_LN_VS_HEALTH_EVT_ID + str(device_data.csp_sdp_ln_health_event_id)
        self.logger.debug(log_msg)

        # Subscribe sdpSubarrayObsState (forwarded attribute) of SdpSubarray
        sdp_obs_state_event_id = self.sdp_subarray_ln_client.subscribe_attribute(const.EVT_SDPSA_OBS_STATE, device_data.obs_state_aggr.observation_state_cb)
        device_data.csp_sdp_ln_obs_state_event_id[device_data.sdp_subarray_ln_proxy] = sdp_obs_state_event_id
        log_msg = const.STR_SDP_LN_VS_HEALTH_EVT_ID + str(device_data.csp_sdp_ln_obs_state_event_id)
        self.logger.debug(log_msg)                                           

        # Subscribe ReceiveAddresses of SdpSubarray
        sdp_receive_addr_event_id = self._sdp_sa_proxy.subscribe_attribute("receiveAddresses", device_data.receive_addresses_cb)
       
    except DevFailed as dev_failed:
        log_msg = const.ERR_SUBS_SDP_SA_LEAF_ATTR + str(dev_failed)
        device_data._read_activity_message = log_msg
        device_data.set_status(const.ERR_SUBS_SDP_SA_LEAF_ATTR)
        self.logger.exception(log_msg)
        tango.Except.throw_exception(const.ERR_SUBS_SDP_SA_LEAF_ATTR,
                                        log_msg,
                                        "SubarrayNode.OnCommand()",
                                        tango.ErrSeverity.ERR)


