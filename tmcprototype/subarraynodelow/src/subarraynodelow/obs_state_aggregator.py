# Standard python import
import logging

# Additional import
from ska.base.control_model import ObsState
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from .device_data import DeviceData
from . import const


class ObsStateAggregator:
    """
    Observation State Aggregator class
    """
    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self._mccs_sa_obs_state = None
        self.mccs_obs_state_event_id = {}
        self.this_server = TangoServerHelper.get_instance()
        self.device_data = DeviceData.get_instance()
        mccs_subarray_ln_fqdn = self.this_server.read_property("MccsSubarrayLNFQDN")
        log_msg = "FQDN: " + str(mccs_subarray_ln_fqdn)
        self.logger.info(log_msg)
        self.mccs_client = TangoClient(str(mccs_subarray_ln_fqdn))

    def subscribe(self):
        # Subscribe mccsSubarrayObsState (forwarded attribute) of mccsSubarray
        mccs_event_id = self.mccs_client.subscribe_attribute(
            const.EVT_MCCSSA_OBS_STATE, self.observation_state_cb
        )
        self.mccs_obs_state_event_id[self.mccs_client] = mccs_event_id
        log_msg = f"{const.STR_SUB_ATTR_MCCS_SALN_OBSTATE_SUCCESS}{self.mccs_obs_state_event_id}"
        self.logger.info(log_msg)

    def unsubscribe(self):
        """
        This function unsubscribes all Observation state events given by the event ids and their
        corresponding DeviceProxy objects.

        :param : None

        :return: None
        """
        for tango_client, event_id in self.mccs_obs_state_event_id.items():
            tango_client.unsubscribe_attribute(event_id)

    def observation_state_cb(self, evt):
        """
        Receives the subscribed MCCS Subarray obsState.

        :param evt: A event on MCCS Subarray ObsState.

        :type: Event object
            It has the following members:

                - date (event timestamp)

                - reception_date (event reception timestamp)

                - type (event type)

                - dev_name (device name)

                - name (attribute name)

                - value (event value)

        :return: None

        :raises: KeyError if error occurs while setting SubarrayNode's ObsState.
        """
        try:
            if not evt.err:
                event_observation_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TMMCCS_MID_SALN in evt.attr_name:
                    # Typacasted the event values to obsState ENUM labels.
                    self._mccs_sa_obs_state = ObsState(event_observation_state)
                    self.this_server.write_attr("activityMessage", f"{const.STR_MCCS_SUBARRAY_OBS_STATE}{event_observation_state}")
                else:
                    self.logger.info(const.EVT_UNKNOWN)
                    self.this_server.write_attr("activityMessage", const.EVT_UNKNOWN)
                self.calculate_observation_state()

            else:
                log_msg = f"{const.ERR_SUBSR_MCCSSA_OBS_STATE}{evt}"
                self.logger.info(log_msg)
                self.this_server.write_attr("activityMessage", log_msg)
        except KeyError as key_error:
            log_msg = f"{const.ERR_MCCS_SUBARRAY_OBS_STATE}{key_error}"
            self.logger.error(log_msg)
            self.this_server.write_attr("activityMessage", f"{const.ERR_MCCS_SUBARRAY_OBS_STATE}{key_error}")

    def calculate_observation_state(self):
        """
        Calculates aggregated observation state of Subarray.
        """
        log_msg = f"MCCS ObsState is: {self._mccs_sa_obs_state}"
        self.logger.info(log_msg)
        if self._mccs_sa_obs_state == ObsState.EMPTY:
            if self.device_data.is_release_resources:
                self.logger.info(
                    "Calling ReleaseAllResource command succeeded() method"
                )
                self.this_server.device.release.succeeded()
        elif self._mccs_sa_obs_state == ObsState.READY:
            if self.device_data.is_scan_completed:
                self.logger.info("Calling EndScan command succeeded() method")
                self.this_server.device.endscan.succeeded()
            else:
                # Configure command success
                self.logger.info("Calling Configure command succeeded() method")
                self.this_server.device.configure.succeeded()
        elif self._mccs_sa_obs_state == ObsState.IDLE:
            if self.device_data.is_end_command:
                # End command success
                self.logger.info("Calling End command succeeded() method")
                self.this_server.device.end.succeeded()
            elif self.device_data.is_obsreset_command_executed:
                # ObsReset command success
                self.logger.info("Calling ObsReset command succeeded() method")
                self.this_server.device.obsreset.succeeded()
            else:
                # Assign Resource command success
                self.logger.info("Calling AssignResource command succeeded() method")
                self.this_server.device.assign.succeeded()
        elif self._mccs_sa_obs_state == ObsState.ABORTED:
            if self.device_data.is_abort_command_executed:
                # Abort command success
                self.logger.info("Calling Abort command succeeded() method")
                self.this_server.device.abort.succeeded()
