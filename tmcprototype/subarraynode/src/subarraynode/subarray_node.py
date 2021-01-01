# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Subarray Node
Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a Subarray.
"""

# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
# Third party imports
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, Group
from tango.server import run,attribute, command, device_property

# Additional imports
from . import const, release, assign_resources_command, release_all_resources_command, configure_command,\
    scan_command, end_scan_command, end_command, on_command, off_command, track_command,\
    abort_command, restart_command, obsreset_command
from .const import PointingState
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, ObsMode, ObsState
from ska.base import SKASubarray
from subarraynode.exceptions import InvalidObsStateError

__all__ = ["SubarrayNode", "main", "assign_resources_command", "release_all_resources_command",
           "configure_command", "scan_command", "end_scan_command", "end_command", "on_command",
           "off_command", "track_command", "abort_command", "restart_command", "obsreset_command"]


class SubarrayHealthState:

    @staticmethod
    def generate_health_state_log_msg(health_state, device_name, event):
        if isinstance(health_state, HealthState):
            return (
                const.STR_HEALTH_STATE + str(device_name) + const.STR_ARROW + str(health_state.name.upper()))
        else:
            return const.STR_HEALTH_STATE_UNKNOWN_VAL + str(event)

    @staticmethod
    def calculate_health_state(health_states):
        """
        Calculates aggregated health state of Subarray.
        """
        unique_states = set(health_states)
        if unique_states == set([HealthState.OK]):
            return HealthState.OK
        elif HealthState.FAILED in unique_states:
            return HealthState.FAILED
        elif HealthState.DEGRADED in unique_states:
            return HealthState.DEGRADED
        else:
            return HealthState.UNKNOWN


class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #
    def command_class_object(self):
        """
        Sets up the command objects
        :return: None
        """
        args = (self, self.state_model, self.logger)
        self.configure_obj = configure_command.ConfigureCommand(*args)
        self.assign_obj = assign_resources_command.AssignResourcesCommand(*args)
        self.release_obj = release_all_resources_command.ReleaseAllResourcesCommand(*args)
        self.scan_obj = scan_command.ScanCommand(*args)
        self.endscan_obj = end_scan_command.EndScanCommand(*args)
        self.end_obj = end_command.EndCommand(*args)
        self.restart_obj = restart_command.RestartCommand(*args)
        self.abort_obj = abort_command.AbortCommand(*args)
        self.init_obj = self.InitCommand(*args)
        self.on_obj = on_command.OnCommand(*args)
        self.off_obj = off_command.OffCommand(*args)
        self.obsreset_obj = obsreset_command.ObsResetCommand(*args)

    def receive_addresses_cb(self, event):
        """
        Retrieves the receiveAddresses attribute of SDP Subarray.

        :param event: A TANGO_CHANGE event on SDP Subarray receiveAddresses attribute.

        :return: None
        """
        if not event.err:
            self._receive_addresses_map = event.attr_value.value
        else:
            log_msg = const.ERR_SUBSR_RECEIVE_ADDRESSES_SDP_SA + str(event)
            self.logger.debug(log_msg)
            self._read_activity_message = log_msg

    def health_state_cb(self, event):
        """
        Retrieves the subscribed health states, aggregates them
        to calculate the overall subarray health state.

        :param event: A TANGO_CHANGE event on Subarray healthState.

        :return: None
        """

        device_name = event.device.dev_name()
        log_msg= "Device name is : " + str(device_name)
        self.logger.debug(log_msg)
        if not event.err:
            event_health_state = event.attr_value.value
            self.subarray_ln_health_state_map[device_name] = event_health_state

            log_message = SubarrayHealthState.generate_health_state_log_msg(
                event_health_state, device_name, event)
            self._read_activity_message = log_message
            self._health_state = SubarrayHealthState.calculate_health_state(
                self.subarray_ln_health_state_map.values())
        else:
            log_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(device_name) + str(event)
            self._read_activity_message = log_message

    def observation_state_cb(self, evt):
        """
        Retrieves the subscribed CSP_Subarray AND SDP_Subarray  obsState.

        :param evt: A TANGO_CHANGE event on CSP and SDP Subarray obsState.

        :return: None
        """
        try:
            if not evt.err:
                self._observetion_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TMCSP_MID_SALN in evt.attr_name:
                    self._csp_sa_obs_state = self._observetion_state
                    self._read_activity_message = const.STR_CSP_SUBARRAY_OBS_STATE + str(
                        self._csp_sa_obs_state)
                elif const.PROP_DEF_VAL_TMSDP_MID_SALN in evt.attr_name:
                    self._sdp_sa_obs_state = self._observetion_state
                    self._read_activity_message = const.STR_SDP_SUBARRAY_OBS_STATE + str(
                        self._sdp_sa_obs_state)
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
        log_msg = "Dish PointingStateMap is :" + str(self.dishPointingStateMap)
        self.logger.info(log_msg)
        log_msg = "self._csp_sa_obs_state is: " + str(self._csp_sa_obs_state)
        self.logger.info(log_msg)
        log_msg = "self._sdp_sa_obs_state is: " + str(self._sdp_sa_obs_state)
        self.logger.info(log_msg)
        for value in list(self.dishPointingStateMap.values()):
            if value == PointingState.TRACK:
                pointing_state_count_track = pointing_state_count_track + 1
            elif value == PointingState.SLEW:
                pointing_state_count_slew = pointing_state_count_slew + 1
            elif value == PointingState.READY:
                pointing_state_count_ready = pointing_state_count_ready + 1
        if ((self._csp_sa_obs_state == ObsState.EMPTY) and (self._sdp_sa_obs_state ==\
                ObsState.EMPTY)):
            if self.is_release_resources:
                self.logger.info("Calling ReleaseAllResource command succeeded() method")
                self.release_obj.succeeded()
            elif self.is_restart_command:
                self.logger.info("Calling Restart command succeeded() method")
                self.restart_obj.succeeded()
                # TODO: As a action for Restart command invoke ReleaseResources command on SubarrayNode

        elif ((self._csp_sa_obs_state == ObsState.ABORTED) and (self._sdp_sa_obs_state == ObsState.ABORTED)):
            if pointing_state_count_ready == len(self.dishPointingStateMap.values()):
                if self.is_abort_command:
                    self.logger.info("Calling ABORT command succeeded() method")
                    self.abort_obj.succeeded()
        elif ((self._csp_sa_obs_state == ObsState.READY) and (self._sdp_sa_obs_state == ObsState.READY)):
            log_msg = "Pointing state in track counts = " + str(pointing_state_count_track)
            self.logger.debug(log_msg)
            log_msg = "No of dished being checked =" + str(len(self.dishPointingStateMap.values()))
            self.logger.debug(log_msg)
            if pointing_state_count_track == len(self.dishPointingStateMap.values()):
                if not self.is_abort_command:
                    if self.is_scan_completed:
                        self.logger.info("Calling EndScan command succeeded() method")
                        self.endscan_obj.succeeded()
                    else:
                        # Configure command success
                        self.logger.info("Calling Configure command succeeded() method")
                        self.configure_obj.succeeded()
        elif ((self._csp_sa_obs_state == ObsState.IDLE) and (self._sdp_sa_obs_state ==\
                ObsState.IDLE)):
            if self.is_end_command:
                if pointing_state_count_ready == len(self.dishPointingStateMap.values()):
                    # End command success
                    self.logger.info("Calling End command succeeded() method")
                    # As a part of end command send Stop track command on dish leaf node
                    #  TODO: Stop track command will be invoked once tango group command issue gets resolved.
                    # self._dish_leaf_node_group.command_inout(const.CMD_STOP_TRACK)
                    self.end_obj.succeeded()
            elif self.is_obsreset_command:
                if pointing_state_count_ready == len(self.dishPointingStateMap.values()):
                    self.logger.info("Calling ObsReset command succeeded() method")
                    self.obsreset_obj.succeeded()

            else:
                # Assign Resource command success
                self.logger.info("Calling AssignResource command succeeded() method")
                self.assign_obj.succeeded()
            # TODO: For future use
            # if len(self.dishPointingStateMap.values()) != 0:
            #     if pointing_state_count_track == len(self.dishPointingStateMap.values()):
            #         if self.only_dishconfig_flag == True:
            #             if not self.isScanRunning:
            #
            #                 self._obs_state = ObsState.READY
            #         else:
            #             self._dish_leaf_node_group.command_inout(const.CMD_STOP_TRACK)
            #             self._obs_state = ObsState.IDLE
            #     else:
            #         # Assign Resource command success
            #         # self._obs_state = ObsState.IDLE
            #         print("Calling AssignResource command succeeded() method")
            #         self.assign_obj.succeeded()

    def get_deviceproxy(self, device_fqdn):
        """
        Returns device proxy for given FQDN.
        """
        retry = 0
        device_proxy = None
        while retry < 3:
            try:
                device_proxy = DeviceProxy(device_fqdn)
                break
            except DevFailed as df:
                self.logger.exception(df)
                if retry >= 2:
                    tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                    "Failed to create DeviceProxy of " + str(device_fqdn),
                                                    "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                retry += 1
                continue
        return device_proxy

    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(const.PROP_DEF_VAL_LEAF_NODE_PREFIX):
                _ = self.subarray_ln_health_state_map.pop(dev_name)

    # TODO for unsubscribing health and obsState events on CSP and SDP
    def _unsubscribe_csp_sdp_state_events(self, proxy_event_id_map):
        """
        This function unsubscribes all events given by the event ids and their
        corresponding DeviceProxy objects.

        :param
            device_proxy: Device Proxy
            proxy_event_id: <event_id>

        :return: None

        """
        for device_proxy, event_id in proxy_event_id_map.items():
            try:
                device_proxy.unsubscribe_event(event_id)
            except DevFailed as dev_failed:
                log_message = "Failed to unsubscribe health state event {}.".format(dev_failed)
                self.logger.error(log_message )
                self._read_activity_message = log_message

    def _unsubscribe_resource_events(self, proxy_event_id_map):
        """
        This function unsubscribes all events given by the event ids and their
        corresponding DeviceProxy objects.

        :param proxy_event_id_map: dict
            A mapping of '<DeviceProxy>': <event_id>.

        :return: None

        """
        for device_proxy, event_id in proxy_event_id_map.items():
            try:
                device_proxy.unsubscribe_event(event_id)
            except DevFailed as dev_failed:
                log_message = "Failed to unsubscribe event {}.".format(dev_failed)
                self.logger.error(log_message )
                self._read_activity_message = log_message

    def __len__(self):
        """
        Returns the number of resources currently assigned. Note that
        this also functions as a boolean method for whether there are
        any assigned resources: ``if len()``.

        :return: number of resources assigned
        :rtype: int
        """

        return len(self._receptor_id_list)

    def pointing_state_cb(self, evt):
        """
        Retrieves the subscribed DishMaster health state, aggregate them to evaluate
        health state of the Subarray.

        :param evt: A TANGO_CHANGE event on DishMaster healthState.

        :return: None

        """
        try:
            log_msg= 'Pointing state Attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._dish_pointing_state = evt.attr_value.value
                self.dishPointingStateMap[evt.device] = self._dish_pointing_state
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

    def validate_obs_state(self):
        if self._obs_state == ObsState.EMPTY:
            self.logger.info("Subarray is in required obsstate, hence resources will be assigned.")
        else:
            self.logger.error("Subarray is not in EMPTY obsState")
            self._read_activity_message = "Error in device obsState."
            raise InvalidObsStateError("Subarray is not in EMPTY obsState, \
                please check the subarray obsState")

    def remove_receptors_from_group(self):
        """
        Deletes tango group of the resources allocated in the subarray.

        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVoid
        :return:
            DevVoid
        """
        if not self._dishLnVsHealthEventID or not self._dishLnVsPointingStateEventID:
            return
        try:
            self._dish_leaf_node_group.remove_all()
            log_message = const.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True))
            self.logger.debug(log_message)
            self._read_activity_message = log_message
            self.logger.info(const.RECEPTORS_REMOVE_SUCCESS)
        except DevFailed as dev_failed:
            log_message = "Failed to remove receptors from the group. {}".format(dev_failed)
            self.logger.error(log_message)
            self._read_activity_message = log_message
            return

        self._unsubscribe_resource_events(self._dishLnVsHealthEventID)
        self._unsubscribe_resource_events(self._dishLnVsPointingStateEventID)

        # clearing dictonaries and lists
        self._dishLnVsHealthEventID.clear()  # Clear eventID dictionary
        self._dishLnVsPointingStateEventID.clear()  # Clear eventID dictionary
        self._health_event_id.clear()
        self._remove_subarray_dish_lns_health_states()
        self.dishPointingStateMap.clear()
        self._pointing_state_event_id.clear()
        self._dish_leaf_node_proxy.clear()
        self._receptor_id_list.clear()
        self.logger.info(const.STR_RECEPTORS_REMOVE_SUCCESS)

    # PROTECTED REGION END #    //  SubarrayNode.class_variable

    # -----------------
    # Device Properties
    # -----------------

    DishLeafNodePrefix = device_property(
        dtype='str', doc="Device name prefix for the Dish Leaf Node",
    )

    CspSubarrayLNFQDN = device_property(

        dtype='str', doc="This property contains the FQDN of the CSP Subarray Leaf Node associated with the "
            "Subarray Node.",
    )

    SdpSubarrayLNFQDN = device_property(
        dtype='str', doc="This property contains the FQDN of the SDP Subarray Leaf Node associated with the "
            "Subarray Node.",
    )

    CspSubarrayFQDN = device_property(
        dtype='str',
    )

    SdpSubarrayFQDN = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype='str',
        doc="ID of ongoing SCAN",
    )

    sbID = attribute(
        dtype='str',
        doc="ID of ongoing Scheduling Block",
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    receptorIDList = attribute(
        dtype=('uint16',),
        max_dim_x=100,
        doc="ID List of the Receptors assigned in the Subarray",
    )

    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKASubarray.InitCommand):
        """
        A class for the TMC SubarrayNode's init_device() method.
        """
        def do(self):
            """
            Initializes the attributes and properties of the Subarray Node.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the error while subscribing the tango attribute
            """
            super().do()
            device = self.target
            device.set_status(const.STR_SA_INIT)
            device._obs_mode = ObsMode.IDLE
            device.isScanRunning = False
            device.is_scan_completed = False
            device.is_end_command = False
            device.is_restart_command = False
            device.is_obsreset_command = False
            device.is_release_resources = False
            device.is_abort_command = False
            device._scan_id = ""
            device._sb_id = ""
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device.scan_duration = 0
            device._receptor_id_list = []
            device.dishPointingStateMap = {}
            device._dish_leaf_node_group = Group(const.GRP_DISH_LEAF_NODE)
            device._dish_leaf_node_proxy = []
            device._health_event_id = []
            device._pointing_state_event_id = []
            device._dishLnVsHealthEventID = {}
            device._dishLnVsPointingStateEventID = {}
            device._cspSdpLnHealthEventID = {}
            device._cspSdpLnObsStateEventID = {}
            device.subarray_ln_health_state_map = {}
            device._subarray_health_state = HealthState.OK  #Aggregated Subarray Health State
            device._csp_sa_obs_state = None
            device._sdp_sa_obs_state = None
            device.only_dishconfig_flag = False
            device.scan_thread = None
            device.command_class_object()
            device._read_activity_message = const.STR_SA_INIT_SUCCESS
            self.logger.info(device._read_activity_message)
            return (ResultCode.OK, device._read_activity_message)

    def always_executed_hook(self):
        """ Internal construct of TANGO. """
        # PROTECTED REGION ID(SubarrayNode.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SubarrayNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SubarrayNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        """ Internal construct of TANGO. Returns the Scan ID.

        EXAMPLE: 123
        Where 123 is a Scan ID from configuration json string.
        """
        # PROTECTED REGION ID(SubarrayNode.scanID_read) ENABLED START #
        return self._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_sbID(self):
        """ Internal construct of TANGO. Returns the scheduling block ID. """
        # PROTECTED REGION ID(SubarrayNode.sbID_read) ENABLED START #
        return self._sb_id
        # PROTECTED REGION END #    //  SubarrayNode.sbID_read

    def read_activityMessage(self):
        """ Internal construct of TANGO. Returns activityMessage.
        Example: "Subarray node is initialized successfully"
        //result occured after initialization of device.
        """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    def read_receptorIDList(self):
        """ Internal construct of TANGO. Returns the receptor IDs allocated to the Subarray.
         """
        # PROTECTED REGION ID(SubarrayNode.receptorIDList_read) ENABLED START #
        return self._receptor_id_list
        # PROTECTED REGION END #    //  SubarrayNode.receptorIDList_read

    # --------
    # Commands
    # --------

    def is_Track_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Track")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="Initial Pointing parameters of Dish - Right Ascension and Declination coordinates.",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Track(self, argin):
        """
        Invokes Track command on the Dishes assigned to the Subarray.
        """
        handler = self.get_command_object("Track")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("Track", track_command.TrackCommand(*args))
        # In order to pass self = subarray node as target device, the assign and release resource commands
        # are registered and inherited from SKASubarray
        self.register_command_object("AssignResources", assign_resources_command.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseAllResources", release_all_resources_command.ReleaseAllResourcesCommand(*args))
        self.register_command_object("Configure", configure_command.ConfigureCommand(*args))
        self.register_command_object("Scan", scan_command.ScanCommand(*args))
        self.register_command_object("EndScan", end_scan_command.EndScanCommand(*args))
        self.register_command_object("End", end_command.EndCommand(*args))
        self.register_command_object("On", on_command.OnCommand(*args))
        self.register_command_object("Off", off_command.OffCommand(*args))
        self.register_command_object("Abort", abort_command.AbortCommand(*args))
        self.register_command_object("Restart", restart_command.RestartCommand(*args))
        self.register_command_object("ObsReset", obsreset_command.ObsResetCommand(*args))

# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(SubarrayNode.main) ENABLED START #
    """
    Runs the SubarrayNode.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: SubarrayNode TANGO object.
    """
    return run((SubarrayNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SubarrayNode.main

if __name__ == '__main__':
    main()
