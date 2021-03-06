from . import const
from .const import PointingState
from ska.base.control_model import ObsState
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from .device_data import DeviceData
import logging


class ObsStateAggregator:
    """
    Observation State Aggregator class
    """
    def __init__(self, logger = None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.csp_sdp_ln_obs_state_event_id = {}
        self.csp_sa_obs_state = None
        self.sdp_sa_obs_state = None
        self.csp_client = None
        self.sdp_client = None
        self.this_server = TangoServerHelper.get_instance()
        self.device_data = DeviceData.get_instance()
        
    
    def subscribe(self):
        self.csp_client = TangoClient(self.device_data.csp_subarray_ln_fqdn)
        self.sdp_client = TangoClient(self.device_data.sdp_subarray_ln_fqdn)
        # Subscribe cspSubarrayObsState (forwarded attribute) of CspSubarray
        csp_event_id = self.csp_client.subscribe_attribute(const.EVT_CSPSA_OBS_STATE, self.observation_state_cb)
        self.csp_sdp_ln_obs_state_event_id[self.csp_client] = csp_event_id
        log_msg = const.STR_CSP_LN_OBS_STATE_EVT_ID + str(self.csp_sdp_ln_obs_state_event_id)
        self.logger.debug(log_msg)

        # Subscribe sdpSubarrayObsState (forwarded attribute) of SdpSubarray
        sdp_event_id = self.sdp_client.subscribe_attribute(const.EVT_SDPSA_OBS_STATE, self.observation_state_cb)
        self.csp_sdp_ln_obs_state_event_id[self.sdp_client] = sdp_event_id
        log_msg = const.STR_SDP_LN_OBS_STATE_EVT_ID + str(self.csp_sdp_ln_obs_state_event_id)
        self.logger.debug(log_msg)


    def unsubscribe(self):
        """
        This function unsubscribes all Observation state events given by the event ids and their
        corresponding DeviceProxy objects.

        :param : None

        :return: None

        """
        for tango_client, event_id in self.csp_sdp_ln_obs_state_event_id.items():
            log_msg = "Unsubscribe ObsState event for " + str(tango_client)
            self.logger.debug(log_msg)
            tango_client.unsubscribe_attribute(event_id)

    
    def observation_state_cb(self, evt):
        """
        Retrieves the subscribed CSP_Subarray AND SDP_Subarray  obsState.

        :param evt: A TANGO_CHANGE event on CSP and SDP Subarray obsState.

        :return: None
        """
        try:
            log_msg = 'Observation State Attribute change event is: ' + str(evt)
            self.logger.debug(log_msg)
            if not evt.err:
                observetion_state = evt.attr_value.value
                log_msg = 'Observation State Attribute value is: ' + str(observetion_state)
                self.logger.info(log_msg)
                if const.PROP_DEF_VAL_TMCSP_MID_SALN in evt.attr_name:
                    self.csp_sa_obs_state = observetion_state
                    self._read_activity_message = const.STR_CSP_SUBARRAY_OBS_STATE + str(
                        self.csp_sa_obs_state)
                elif const.PROP_DEF_VAL_TMSDP_MID_SALN in evt.attr_name:
                    self.sdp_sa_obs_state = observetion_state
                    self._read_activity_message = const.STR_SDP_SUBARRAY_OBS_STATE + str(
                        self.sdp_sa_obs_state)
                else:
                    self.logger.debug(const.EVT_UNKNOWN)
                    self._read_activity_message = const.EVT_UNKNOWN
                self.calculate_observation_state()

            else:
                log_msg = const.ERR_SUBSR_CSPSDPSA_OBS_STATE + str(evt)
                self.logger.debug(log_msg)
                self._read_activity_message = log_msg
        except KeyError as key_error:
            log_msg = const.ERR_CSPSDP_SUBARRAY_OBS_STATE + str(key_error)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_CSPSDP_SUBARRAY_OBS_STATE + str(key_error)

    def calculate_observation_state(self):
        """
        Calculates aggregated observation state of Subarray.
        """
        pointing_state_count_track = 0
        pointing_state_count_slew = 0
        pointing_state_count_ready = 0
        log_msg = "Dish PointingStateMap is :" + str(self.device_data.dishPointingStateMap)
        self.logger.info(log_msg)
        log_msg = "self._csp_sa_obs_state is: " + str(self.csp_sa_obs_state)
        self.logger.info(log_msg)
        log_msg = "self._sdp_sa_obs_state is: " + str(self.sdp_sa_obs_state)
        self.logger.info(log_msg)
        for value in list(self.device_data.dishPointingStateMap.values()):
            if value == PointingState.TRACK:
                pointing_state_count_track = pointing_state_count_track + 1
            elif value == PointingState.SLEW:
                pointing_state_count_slew = pointing_state_count_slew + 1
            elif value == PointingState.READY:
                pointing_state_count_ready = pointing_state_count_ready + 1
        if ((self.csp_sa_obs_state == ObsState.EMPTY) and (self.sdp_sa_obs_state ==\
                ObsState.EMPTY)):
            if self.device_data.is_release_resources:
                self.logger.info("Calling ReleaseAllResource command succeeded() method")
                self.this_server.device.release.succeeded()
            elif self.device_data.is_restart_command:
                self.logger.info("Calling Restart command succeeded() method")
                self.this_server.device.restart.succeeded()
                # TODO: As a action for Restart command invoke ReleaseResources command on SubarrayNode
        elif ((self.csp_sa_obs_state == ObsState.ABORTED) and (self.sdp_sa_obs_state == ObsState.ABORTED)):
            if pointing_state_count_ready == len(self.device_data.dishPointingStateMap.values()):
                if self.device_data.is_abort_command:
                    self.logger.info("Calling ABORT command succeeded() method")
                    self.this_server.device.abort.succeeded()
        elif ((self.csp_sa_obs_state == ObsState.READY) and (self.sdp_sa_obs_state == ObsState.READY)):
            log_msg = "Pointing state in track counts = " + str(pointing_state_count_track)
            self.logger.debug(log_msg)
            log_msg = "No of dishes being checked =" + str(len(self.device_data.dishPointingStateMap.values()))
            self.logger.debug(log_msg)
            if pointing_state_count_track == len(self.device_data.dishPointingStateMap.values()):
                if not self.device_data.is_abort_command:
                    if self.device_data.is_scan_completed:
                        self.logger.info("Calling EndScan command succeeded() method")
                        self.this_server.device.endscan.succeeded()
                    else:
                        # Configure command success
                        self.logger.info("Calling Configure command succeeded() method")
                        self.this_server.device.configure.succeeded()
        elif ((self.csp_sa_obs_state == ObsState.IDLE) and (self.sdp_sa_obs_state ==\
                ObsState.IDLE)):
            if self.device_data.is_end_command:
                if pointing_state_count_ready == len(self.device_data.dishPointingStateMap.values()):
                    # End command success
                    self.logger.info("Calling End command succeeded() method")
                    # As a part of end command send Stop track command on dish leaf node
                    #  TODO: Stop track command will be invoked once tango group command issue gets resolved.
                    # self._dish_leaf_node_group.command_inout(const.CMD_STOP_TRACK)
                    self.this_server.device.end.succeeded()
            elif self.device_data.is_obsreset_command:
                if pointing_state_count_ready == len(self.device_data.dishPointingStateMap.values()):
                    self.logger.info("Calling ObsReset command succeeded() method")
                    self.this_server.device.obsreset.succeeded()
            else:
                # Assign Resource command success
                self.logger.info("Calling AssignResource command succeeded() method")
                self.this_server.device.assign.succeeded()
                self.logger.info("AssignResource command succeeded() method executed")


    def pointing_state_cb(self, evt):
        """
        Retrieves the s_dish_pointing_stateubscribed DishMaster health state, aggregate them to evaluate
        health state of the Subarray.

        :param evt: A TANGO_CHANGE event on DishMaster healthState.

        :return: None

        """
        try:
            log_msg= 'Pointing state Attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._dish_pointing_state = evt.attr_value.value
                log_msg= 'in Obs_state_cb dishPointingStateMap : ' + str(self.device_data.dishPointingStateMap)
                self.logger.info(log_msg)
                self.device_data.dishPointingStateMap[evt.device] = self._dish_pointing_state
                if self._dish_pointing_state == PointingState.READY:
                    str_log = const.STR_POINTING_STATE + str(evt.device) + const.STR_READY
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                elif self._dish_pointing_state == PointingState.SLEW:
                    str_log = const.STR_POINTING_STATE + str(evt.device) + const.STR_SLEW
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                elif self._dish_pointing_state == PointingState.TRACK:
                    str_log = const.STR_POINTING_STATE + str(evt.device) + const.STR_TRACK
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                elif self._dish_pointing_state == PointingState.SCAN:
                    str_log = const.STR_POINTING_STATE + str(evt.device) + const.STR_SCAN
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                else:
                    self.logger.debug(const.STR_HEALTH_STATE_UNKNOWN_VAL, evt)
                    self._read_activity_message = const.STR_POINTING_STATE_UNKNOWN_VAL + str(evt)
                self.calculate_observation_state()
            else:
                log_msg = const.ERR_SUBSR_DSH_POINTING_STATE + str(evt.errors)
                self.logger.debug(log_msg)
                self._read_activity_message = const.ERR_SUBSR_DSH_POINTING_STATE + str(evt.errors)
        except KeyError as key_err:
            log_msg = const.ERR_SETPOINTING_CALLBK + str(key_err)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_SETPOINTING_CALLBK + str(key_err)

    def subscribe_dish_pointing_state(self, dish_ln_client):
        dish_event_id = dish_ln_client.subscribe_attribute(const.EVT_DISH_POINTING_STATE, self.pointing_state_cb)
        self.device_data._dishLnVsPointingStateEventID[dish_ln_client] = dish_event_id
        log_msg = const.STR_DISH_LN_VS_POINTING_STATE_EVT_ID + str(self.device_data._dishLnVsPointingStateEventID)
        self.logger.debug(log_msg)

    def unsubscribe_dish_pointing_state(self):
        for dish_ln_client in self.device_data._dishLnVsPointingStateEventID:
            dish_ln_client.unsubscribe_attribute(self.device_data._dishLnVsPointingStateEventID[dish_ln_client])

