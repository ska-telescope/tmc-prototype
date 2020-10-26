"""
OnCommand class for SubarrayNode
"""
# Tango imports
import tango
from tango import DevFailed, DeviceProxy, EventType

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from ska.base.control_model import HealthState, ObsMode, ObsState


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
        device = self.target
        device.is_restart_command = False
        device.is_release_resources = False
        device.is_abort_command = False
        device.is_obsreset_command = False

        # device.resultVal = device._proxy_creation()

        try:
            device._csp_subarray_ln_proxy = None
            log_msg = const.STR_SA_PROXY_INIT # + str(device.CspSubarrayLNFQDN)
            device._csp_subarray_ln_proxy = device.get_deviceproxy(device.CspSubarrayLNFQDN)
            self.logger.info(log_msg)
            # Create proxy for SDP Subarray Leaf Node
            device._sdp_subarray_ln_proxy = None
            log_msg = const.STR_SA_PROXY_INIT # + str(device.CspSubarrayLNFQDN)
            device._sdp_subarray_ln_proxy = device.get_deviceproxy(device.SdpSubarrayLNFQDN)
            self.logger.info(log_msg)
            device._csp_sa_proxy = device.get_deviceproxy(device.CspSubarrayFQDN)
            device._sdp_sa_proxy = device.get_deviceproxy(device.SdpSubarrayFQDN)
    
        except DevFailed as dev_failed:
            log_msg = const.ERR_PROXY_CREATE
            self.logger.debug(log_msg)
            tango.Except.throw_exception(dev_failed[0].desc, "Failed to create proxy on SubarrayNode.",
                                         "SubarrayNode.On()", tango.ErrSeverity.ERR)

        # if(device.resultVal):
        #     log_msg = "=====result of proxy is true"
        #     self.logger.info(log_msg)

        try:
            device.subarray_ln_health_state_map[device._csp_subarray_ln_proxy.dev_name()] = (
                HealthState.UNKNOWN)
            # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
            self._event_id = device._csp_subarray_ln_proxy.subscribe_event(
                const.EVT_CSPSA_HEALTH, EventType.CHANGE_EVENT,device.health_state_cb,
                stateless=True)
            device._cspSdpLnHealthEventID[device._csp_subarray_ln_proxy] = self._event_id
            log_msg = const.STR_CSP_LN_VS_HEALTH_EVT_ID + str(device._cspSdpLnHealthEventID)
            self.logger.debug(log_msg)

            # Subscribe cspSubarrayObsState (forwarded attribute) of CspSubarray
            self._event_id = device._csp_subarray_ln_proxy.subscribe_event(const.EVT_CSPSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                            device.observation_state_cb, stateless=True)
            device._cspSdpLnObsStateEventID[device._csp_subarray_ln_proxy] = self._event_id
            log_msg = const.STR_CSP_LN_VS_HEALTH_EVT_ID + str(device._cspSdpLnObsStateEventID)
            self.logger.debug(log_msg)

            device.set_status(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
            self.logger.info(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBS_CSP_SA_LEAF_ATTR + str(dev_failed)
            device._read_activity_message = log_msg
            device.set_status(const.ERR_SUBS_CSP_SA_LEAF_ATTR)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_SUBS_CSP_SA_LEAF_ATTR,
                                            log_msg,
                                            "SubarrayNode.InitCommand",
                                            tango.ErrSeverity.ERR)

        try:
            device.subarray_ln_health_state_map[device._sdp_subarray_ln_proxy.dev_name()] = (
                HealthState.UNKNOWN)
            # Subscribe sdpSubarrayHealthState (forwarded attribute) of SdpSubarray
            self._event_id = device._sdp_subarray_ln_proxy.subscribe_event(const.EVT_SDPSA_HEALTH, EventType.CHANGE_EVENT,
                                                        device.health_state_cb, stateless=True)
            device._cspSdpLnHealthEventID[device._sdp_subarray_ln_proxy] = self._event_id   
            log_msg = const.STR_SDP_LN_VS_HEALTH_EVT_ID + str(device._cspSdpLnHealthEventID)
            self.logger.debug(log_msg)

            # Subscribe sdpSubarrayObsState (forwarded attribute) of SdpSubarray
            self._event_id = device._sdp_subarray_ln_proxy.subscribe_event(const.EVT_SDPSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                        device.observation_state_cb, stateless=True)
            device._cspSdpLnObsStateEventID[device._sdp_subarray_ln_proxy] = self._event_id 
            log_msg = const.STR_SDP_LN_VS_HEALTH_EVT_ID + str(device._cspSdpLnObsStateEventID)
            self.logger.debug(log_msg)                                           

            # Subscribe ReceiveAddresses of SdpSubarray
            device._sdp_sa_proxy.subscribe_event("receiveAddresses", EventType.CHANGE_EVENT,
                                                device.receive_addresses_cb, stateless=True)
            device.set_status(const.STR_SDP_SA_LEAF_INIT_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBS_SDP_SA_LEAF_ATTR + str(dev_failed)
            device._read_activity_message = log_msg
            device.set_status(const.ERR_SUBS_SDP_SA_LEAF_ATTR)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.ERR_SUBS_SDP_SA_LEAF_ATTR,
                                            log_msg,
                                            "SubarrayNode.InitCommand",
                                            tango.ErrSeverity.ERR)

        try:
            device._csp_subarray_ln_proxy.On()
            device._sdp_subarray_ln_proxy.On()
            message = "On command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)
        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
            self.logger.debug(log_msg)
            self._read_activity_message = log_msg
            tango.Except.throw_exception(dev_failed[0].desc, "Failed to invoke On command on SubarrayNode.",
                                        "SubarrayNode.On()", tango.ErrSeverity.ERR)

            
    # def _proxy_creation(self):
    #     device =self.target
    #      # Create proxy for CSP Subarray Leaf Node
    #     try:
    #         device._csp_subarray_ln_proxy = None
    #         log_msg = const.STR_SA_PROXY_INIT + device.CspSubarrayLNFQDN
    #         device._csp_subarray_ln_proxy = device.get_deviceproxy(device.CspSubarrayLNFQDN)
    #         self.logger.info(log_msg)
    #         # Create proxy for SDP Subarray Leaf Node
    #         device._sdp_subarray_ln_proxy = None
    #         log_msg = const.STR_SA_PROXY_INIT + device.CspSubarrayLNFQDN
    #         device._sdp_subarray_ln_proxy = device.get_deviceproxy(device.SdpSubarrayLNFQDN)
    #         self.logger.info(log_msg)
    #         device._csp_sa_proxy = device.get_deviceproxy(device.CspSubarrayFQDN)
    #         device._sdp_sa_proxy = device.get_deviceproxy(device.SdpSubarrayFQDN)
    #         return true
    #     except DevFailed as dev_failed:
    #         log_msg = const.ERR_PROXY_CREATE
    #         self.logger.debug(log_msg)
    #         tango.Except.throw_exception(dev_failed[0].desc, "Failed to create proxy on SubarrayNode.",
    #                                      "SubarrayNode.On()", tango.ErrSeverity.ERR)

