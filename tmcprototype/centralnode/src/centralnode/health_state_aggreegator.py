"""
health_state_aggreegator class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import ast

# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from ska.base.control_model import HealthState, ObsState
from . import const, release
from centralnode.device_data import DeviceData
from centralnode.tango_client import tango_client
# PROTECTED REGION END #    //  CentralNode.additional_import

class HealthStateAggreegator:
    """
    Aggrergator class for health state event supscription and health state
    callback.
    """
    def do(self):
        """
        Create proxy of sdp,csp and HealthState event subscription.

        :return: None
        """
        self.logger.info(type(self.target))
        self.csp_proxy()
        self.csp_health_subscribe_event()
        self.sdp_proxy()
        self.sdp_health_subscribe_event()

    def csp_proxy(self):
        """
        Crate CspMasterLeafNode proxy

        :return: None

        :raises: DevFailed if error occurs while creating proxy.
        """
        device_data = self.target
        try:
            self.csp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)

        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
                                         tango.ErrSeverity.ERR)

    def csp_health_subscribe_event(self):
        """
        Method for event subscription on CspMasterLeafNode.

        :return: None
        """
        device_data = self.target
        device_data.sdp_event_id = self.sdp_mln_client.subscribe_event(const.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                                       EventType.CHANGE_EVENT,
                                                                       self.health_state_cb, stateless=True)

    def sdp_proxy(self):
        """
       Crate SdpMasterLeafNode proxy

       :return: None

       :raises: DevFailed if error occurs while creating proxy.
       """
        try:
            self.sdp_mln_client = TangoClient(device_data.sdp_master_ln_fqdn)

        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
                                         tango.ErrSeverity.ERR)

    def sdp_health_subscribe_event(self):
        """
        Method for event subscription on SdpMasterLeafNode.

        :return: None
        """
        device_data = self.target
        device_data.sdp_event_id = self.sdp_mln_client.subscribe_event(const.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                                       EventType.CHANGE_EVENT,
                                                                       self.health_state_cb, stateless=True)

    def health_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None

        :raises: KeyError if error occurs while setting Subarray healthState
        """
        device_data = self.target
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    device_data._subarray1_health_state = health_state
                    device_data.subarray_health_state_map[evt.device] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    device_data._subarray2_health_state = health_state
                    device_data.subarray_health_state_map[evt.device] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    device_data._subarray3_health_state = health_state
                    device_data.subarray_health_state_map[evt.device] = health_state
                elif device_data.CspMasterLeafNodeFQDN in evt.attr_name:
                    device_data._csp_master_leaf_health = health_state
                elif device_data.SdpMasterLeafNodeFQDN in evt.attr_name:
                    device_data._sdp_master_leaf_health = health_state
                else:
                    self.logger.debug(const.EVT_UNKNOWN)
                    # TODO: For future reference
                    # self._read_activity_message = const.EVT_UNKNOWN

                counts = {
                    HealthState.OK: 0,
                    HealthState.DEGRADED: 0,
                    HealthState.FAILED: 0,
                    HealthState.UNKNOWN: 0
                }

                for subsystem_health_field_name in ['csp_master_leaf_health', 'sdp_master_leaf_health']:
                    health_state = getattr(self, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1

                for subarray_health_state in list(self.subarray_health_state_map.values()):
                    counts[subarray_health_state] += 1

                # Calculating health_state for SubarrayNode, CspMasterLeafNode, SdpMasterLeafNode
                if counts[HealthState.OK] == len(list(self.subarray_health_state_map.values())) + 2:
                    device_data._telescope_health_state = HealthState.OK
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_OK
                elif counts[HealthState.FAILED] != 0:
                    device_data._telescope_health_state = HealthState.FAILED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_FAILED
                elif counts[HealthState.DEGRADED] != 0:
                    device_data._telescope_health_state = HealthState.DEGRADED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_DEGRADED
                else:
                    device_data._telescope_health_state = HealthState.UNKNOWN
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_UNKNOWN
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_UNKNOWN
            else:
                # TODO: For future reference
                device_data._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            # TODO: For future reference
            device_data._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)
