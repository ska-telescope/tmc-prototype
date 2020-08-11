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

from __future__ import print_function
from __future__ import absolute_import


# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
import random
import string
import json
import threading
# Tango imports
import tango
from tango import DevState, AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property

# Additional import
from . import const, release, assign_resources, release_all_resources, configure, scan
from .const import PointingState
from ska.base.commands import ResultCode, ResponseCommand
from ska.base.control_model import HealthState, ObsMode, ObsState
from ska.base import SKASubarray
from subarraynode.exceptions import InvalidObsStateError

__all__ = ["SubarrayNode", "main", "assign_resources", "release_all_resources", "configure", "scan"]


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
        self.configure_obj = configure.ConfigureCommand(*args)
        self.assign_obj = assign_resources.AssignResourcesCommand(*args)
        self.release_obj = release_all_resources.ReleaseAllResourcesCommand(*args)
        self.scan_obj = scan.ScanCommand(*args)
        self.endscan_obj = self.EndScanCommand(*args)
        self.end_obj = self.EndCommand(*args)
        self.restart_obj = self.RestartCommand(*args)
        self.abort_obj = self.AbortCommand(*args)
        self.init_obj = self.InitCommand(*args)


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
        exception_message = []
        exception_count = 0
        try:
            device_name = event.device.dev_name()
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
        except Exception as except_occured:
            [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                                                  exception_message,
                                                                                  exception_count,
                                                                                  const.ERR_AGGR_HEALTH_STATE)

    def observation_state_cb(self, evt):
        """
        Retrieves the subscribed CSP_Subarray AND SDP_Subarray  obsState.

        :param evt: A TANGO_CHANGE event on CSP and SDP Subarray obsState.

        :return: None
        """
        exception_message = []
        exception_count = 0
        try:
            log_msg = 'Observation State Attribute change event is: ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._observetion_state = evt.attr_value.value
                log_msg = 'Observation State Attribute value is: ' + str(self._observetion_state)
                self.logger.info(log_msg)
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
        except Exception as except_occured:
            [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                                                  exception_message,
                                                                                  exception_count,
                                                                                  const.ERR_AGGR_OBS_STATE)

    def calculate_observation_state(self):
        """
        Calculates aggregated observation state of Subarray.
        """
        self.logger.info("\n\n In Calculate observation state method")
        pointing_state_count_track = 0
        pointing_state_count_slew = 0
        pointing_state_count_ready = 0
        log_msg = "Dish PointingStateMap is :" + str(self.dishPointingStateMap)
        self.logger.info(log_msg)
        for value in list(self.dishPointingStateMap.values()):
            if value == PointingState.TRACK:
                pointing_state_count_track = pointing_state_count_track + 1
            elif value == PointingState.SLEW:
                pointing_state_count_slew = pointing_state_count_slew + 1
            elif value == PointingState.READY:
                pointing_state_count_ready = pointing_state_count_ready + 1
        if self._csp_sa_obs_state == ObsState.EMPTY and self._sdp_sa_obs_state ==\
                ObsState.EMPTY:
            if self.is_release_resources:
                self.logger.info("Calling ReleaseAllResource command succeeded() method")
                self.release_obj.succeeded()
            elif self.is_restart_command:
                self.logger.info("Calling Restart command succeeded() method")
                self.restart_obj.succeeded()
                # TODO: As a action for Restart command invoke ReleaseResources command on SubarrayNode
        elif self._csp_sa_obs_state == ObsState.ABORTED and self._sdp_sa_obs_state == \
                ObsState.ABORTED:
            if self.is_abort_command:
                self.logger.info("Calling ABORT command succeeded() method")
                self.abort_obj.succeeded()
        elif self._csp_sa_obs_state == ObsState.READY and self._sdp_sa_obs_state ==\
                ObsState.READY:
            log_msg = "Pointing state in track counts = " + str(pointing_state_count_track)
            self.logger.debug(log_msg)
            log_msg = "No of dished being checked =" + str(len(self.dishPointingStateMap.values()))
            self.logger.debug(log_msg)
            if pointing_state_count_track == len(self.dishPointingStateMap.values()):
                if self.is_scan_completed:
                    self.logger.info("Calling EndScan command succeeded() method")
                    self.endscan_obj.succeeded()
                else:
                    # Configure command success
                    self.logger.info("Calling Configure command succeeded() method")
                    self.configure_obj.succeeded()
        elif self._csp_sa_obs_state == ObsState.IDLE and self._sdp_sa_obs_state ==\
                ObsState.IDLE:
            if self.is_end_command:
                if pointing_state_count_ready == len(self.dishPointingStateMap.values()):
                    # End command success
                    self.logger.info("Calling End command succeeded() method")
                    # As a part of end command send Stop track command on dish leaf node
                    #  TODO: Stop track command will be invoked once tango group command issue gets resolved.
                    # self._dish_leaf_node_group.command_inout(const.CMD_STOP_TRACK)
                    self.end_obj.succeeded()
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

    def _handle_generic_exception(self, exception, excpt_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(exception)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(exception)
        excpt_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [excpt_msg_list, exception_count]

    def _handle_devfailed_exception(self, df, excpt_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(df)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(df)
        excpt_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [excpt_msg_list, exception_count]

    def throw_exception(self, excpt_msg_list, read_actvity_msg):
        err_msg = ''
        for item in excpt_msg_list:
            err_msg += item + "\n"
        tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)

    def create_csp_ln_proxy(self):
        """
        Creates proxy of CSP Subarray Leaf Node.
        """
        retry = 0
        proxy_created_flag = False
        while retry < 3:
            try:
                self._csp_subarray_ln_proxy = DeviceProxy(self.CspSubarrayLNFQDN)
                proxy_created_flag = True
                break
            except Exception:
                retry += 1
                continue

        return proxy_created_flag

    def create_sdp_ln_proxy(self):
        """
         Creates proxy of SDP Subarray Leaf Node.
        """
        retry = 0
        proxy_created_flag = False
        while retry < 3:
            try:
                self._sdp_subarray_ln_proxy = DeviceProxy(self.SdpSubarrayLNFQDN)
                proxy_created_flag = True
                break
            except tango.DevFailed:
                retry += 1
                continue

        return proxy_created_flag

    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(const.PROP_DEF_VAL_LEAF_NODE_PREFIX):
                _ = self.subarray_ln_health_state_map.pop(dev_name)

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

    def call_end_scan_command(self):
        self.endscan_obj.do()

    def pointing_state_cb(self, evt):
        """
        Retrieves the subscribed DishMaster health state, aggregate them to evaluate
        health state of the Subarray.

        :param evt: A TANGO_CHANGE event on DishMaster healthState.

        :return: None

        """
        exception_message = []
        exception_count = 0
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
        except Exception as except_occured:
            [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                                                  exception_message,
                                                                                  exception_count,
                                                                                  const.ERR_AGGR_POINTING_STATE)

    def validate_obs_state(self):
        if self._obs_state == ObsState.EMPTY:
            self.logger.info("Subarray is in required obsstate, hence resources will be assigned.")
        else:
            self.logger.error("Subarray is not in EMPTY obsState")
            self._read_activity_message = "Error in device obsState."
            raise InvalidObsStateError("Subarray is not in EMPTY obsState, \
                please check the subarray obsState")

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
            exception_message = []
            exception_count = 0
            device = self.target
            device.set_status(const.STR_SA_INIT)
            device._obs_mode = ObsMode.IDLE
            device.isScanRunning = False
            device.is_scan_completed = False
            device.is_end_command = False
            device.is_restart_command = False
            device.is_release_resources = False
            device.is_abort_command = False
            device._scan_id = ""
            device._sb_id = ""
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device.scan_duration = 0
            device._receptor_id_list = []
            device.dishPointingStateMap = {}
            device._dish_leaf_node_group = tango.Group(const.GRP_DISH_LEAF_NODE)
            device._dish_leaf_node_proxy = []
            device._health_event_id = []
            device._pointing_state_event_id = []
            device._dishLnVsHealthEventID = {}
            device._dishLnVsPointingStateEventID = {}
            device.subarray_ln_health_state_map = {}
            device._subarray_health_state = HealthState.OK  #Aggregated Subarray Health State
            device._csp_sa_obs_state = None
            device._sdp_sa_obs_state = None
            device.only_dishconfig_flag = False
            device.scan_thread = None

            # Create proxy for CSP Subarray Leaf Node
            device._csp_subarray_ln_proxy = None
            device.create_csp_ln_proxy()
            # Create proxy for SDP Subarray Leaf Node
            device._sdp_subarray_ln_proxy = None
            device.create_sdp_ln_proxy()
            device._csp_sa_proxy = DeviceProxy(device.CspSubarrayFQDN)
            device._sdp_sa_proxy = DeviceProxy(device.SdpSubarrayFQDN)
            device.command_class_object()
            try:
                device.subarray_ln_health_state_map[device._csp_subarray_ln_proxy.dev_name()] = (
                    HealthState.UNKNOWN)
                # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
                device._csp_subarray_ln_proxy.subscribe_event(
                    const.EVT_CSPSA_HEALTH, EventType.CHANGE_EVENT,device.health_state_cb,
                    stateless=True)
                # Subscribe cspSubarrayObsState (forwarded attribute) of CspSubarray
                device._csp_subarray_ln_proxy.subscribe_event(const.EVT_CSPSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                              device.observation_state_cb, stateless=True)
                device.set_status(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
                self.logger.info(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBS_CSP_SA_LEAF_ATTR + str(dev_failed)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                    exception_message, exception_count, const.ERR_SUBS_CSP_SA_LEAF_ATTR)
                device.set_status(const.ERR_SUBS_CSP_SA_LEAF_ATTR)
                self.logger.error(const.ERR_CSP_SA_LEAF_INIT)
                device.throw_exception(exception_message, device._read_activity_message)

            try:
                device.subarray_ln_health_state_map[device._sdp_subarray_ln_proxy.dev_name()] = (
                    HealthState.UNKNOWN)
                # Subscribe sdpSubarrayHealthState (forwarded attribute) of SdpSubarray
                device._sdp_subarray_ln_proxy.subscribe_event(const.EVT_SDPSA_HEALTH, EventType.CHANGE_EVENT,
                                                            device.health_state_cb, stateless=True)
                # Subscribe sdpSubarrayObsState (forwarded attribute) of SdpSubarray
                device._sdp_subarray_ln_proxy.subscribe_event(const.EVT_SDPSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                            device.observation_state_cb, stateless=True)
                # device._sdp_sa_proxy.subscribe_event('state', EventType.CHANGE_EVENT,
                #                                    device.device_state_cb, stateless=True)
                # Subscribe ReceiveAddresses of SdpSubarray
                device._sdp_sa_proxy.subscribe_event("receiveAddresses", EventType.CHANGE_EVENT,
                                                   device.receive_addresses_cb, stateless=True)

                device.set_status(const.STR_SDP_SA_LEAF_INIT_SUCCESS)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBS_SDP_SA_LEAF_ATTR + str(dev_failed)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                exception_message, exception_count, const.ERR_SUBS_SDP_SA_LEAF_ATTR)
                device.set_status(const.ERR_SUBS_SDP_SA_LEAF_ATTR)
                device.throw_exception(exception_message, device._read_activity_message)

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

    def call_stop_track_command(self):
        # TODO: Getting exception while running test cases using device mocking
        self._dish_leaf_node_group.command_inout(const.CMD_STOP_TRACK)
        self.logger.info(const.STR_CMD_STOP_TRACK_INV_DLN)

    class EndCommand(SKASubarray.EndCommand):
        """
        A class for SubarrayNode's End() command.
        """
        def do(self):
            """
            This command on Subarray Node invokes EndSB command on CSP Subarray Leaf Node and SDP
            Subarray Leaf Node, and stops tracking of all the assigned dishes.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: Exception if command execution throws any generic type of exception
                    DevFailed if the command execution is not successful
            """
            device = self.target
            device.is_end_command = False
            exception_message = []
            exception_count = 0
            try:
                self.logger.info("End command invoked on SubarrayNode.")
                device._sdp_subarray_ln_proxy.command_inout(const.CMD_ENDSB)
                self.logger.info(const.STR_CMD_ENDSB_INV_SDP)
                device._csp_subarray_ln_proxy.command_inout(const.CMD_GOTOIDLE)
                self.logger.info(const.STR_CMD_GOTOIDLE_INV_CSP)
                # TODO: Uncomment this after resolving issues
                device.call_stop_track_command()
                device._read_activity_message = const.STR_ENDSB_SUCCESS
                self.logger.info(const.STR_ENDSB_SUCCESS)
                device.set_status(const.STR_ENDSB_SUCCESS)
                device.is_end_command = True
                return (ResultCode.OK, const.STR_ENDSB_SUCCESS)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                exception_message, exception_count, const.ERR_ENDSB_INVOKING_CMD)
            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, const.ERR_ENDSB_INVOKING_CMD)
            # throw exception:
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_ENDSB_EXEC)
            # PROTECTED REGION END #    //  SubarrayNode.EndSB

    class AbortCommand(SKASubarray.AbortCommand):
        """
        A class for SubarrayNode's Abort() command.
        """
        def do(self):
            """
            This command on Subarray Node invokes Abort command on CSP Subarray Leaf Node and SDP
            Subarray Leaf Node, and stops tracking of all the assigned dishes.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs in invoking command on any of the devices like CSPSubarrayLeafNode,
                    SDPSubarrayLeafNode or DishLeafNode
            """
            device = self.target
            exception_message = []
            exception_count = 0
            try:
                device._sdp_subarray_ln_proxy.command_inout(const.CMD_ABORT)
                self.logger.info(const.STR_CMD_ABORT_INV_SDP)
                device._csp_subarray_ln_proxy.command_inout(const.CMD_ABORT)
                self.logger.info(const.STR_CMD_ABORT_INV_CSP)
                device._dish_leaf_node_group.command_inout(const.CMD_ABORT)
                device._read_activity_message = const.STR_ABORT_SUCCESS
                self.logger.info(const.STR_ABORT_SUCCESS)
                device.set_status(const.STR_ABORT_SUCCESS)
                device.is_abort_command = True
                return (ResultCode.STARTED, const.STR_ABORT_SUCCESS)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                exception_message, exception_count, const.ERR_ABORT_INVOKING_CMD)
            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, const.ERR_ABORT_INVOKING_CMD)

            # throw exception:
            if exception_count > 0:
                device.throw_exception(exception_message, const.ERR_ABORT_INVOKING_CMD)
            # PROTECTED REGION END #    //  SubarrayNode.Abort

    class TrackCommand(ResponseCommand):
        """
        A class for SubarrayNode's Track command.
        """
        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state.

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command TrackCommand is not allowed in current state.",
                                             "Failed to invoke TrackCommand command on DishLeafNode.",
                                             "SubarrayNode.TrackComamnd()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self, argin):
            """ Invokes Track command on the Dishes assigned to the Subarray.

            :param argin: DevString

            Example:
            radec|21:08:47.92|-88:57:22.9 as argin
            Argin to be provided is the Ra and Dec values where first value is tag that is radec, second value is Ra
            in Hr:Min:Sec, and third value is Dec in Deg:Min:Sec.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device = self.target
            exception_message = []
            exception_count = 0
            log_msg = "Track:", argin
            self.logger.debug(log_msg)
            try:
                device._read_activity_message = const.STR_TRACK_IP_ARG + argin
                cmd_input = [argin]
                cmdData = tango.DeviceData()
                cmdData.insert(tango.DevVarStringArray, cmd_input)
                device._dish_leaf_node_group.command_inout(const.CMD_TRACK, cmdData)
                device._scan_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                self.logger.info(const.STR_TRACK_CMD_INVOKED_SA)
                return (ResultCode.OK, const.STR_TRACK_CMD_INVOKED_SA)
            except tango.DevFailed as devfailed:
                exception_message.append(const.ERR_TRACK_CMD + ": " + \
                               str(devfailed.args[0].desc))
                exception_count += 1
            except Exception as except_occured:
                str_log = const.ERR_TRACK_CMD + "\n" + str(except_occured)
                self.logger.error(str_log)
                self._read_activity_message = const.ERR_TRACK_CMD + str(except_occured)
                self.logger.error(const.ERR_TRACK_CMD)
                exception_message.append(const.ERR_TRACK_CMD + ": " + \
                                 str(except_occured.args[0].desc))
                exception_count += 1
            # throw exception
            if exception_count > 0:
                err_msg = ' '
                for item in exception_message:
                    err_msg += item + "\n"
                tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg,
                                             const.STR_TRACK_EXEC, tango.ErrSeverity.ERR)
            # PROTECTED REGION END #    //  SubarrayNode.Track

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
            exception_message = []
            exception_count = 0
            try:
                device._csp_subarray_ln_proxy.On()
                device._sdp_subarray_ln_proxy.On()
                message = "On command completed OK"
                self.logger.info(message)
                return (ResultCode.OK, message)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_INVOKING_ON_CMD)

    class OffCommand(SKASubarray.OffCommand):
        """
        A class for the SubarrayNodes's Off() command.
        """
        def do(self):
            """
            This command invokes Off Command on CSPSubarray and SDPSubarray through respective leaf nodes. This comamnd
            changes Subaray device state from ON to OFF.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if the command execution is not successful
            """
            device = self.target
            exception_message = []
            exception_count = 0
            try:
                device._csp_subarray_ln_proxy.Off()
                device._sdp_subarray_ln_proxy.Off()
                message = "Off command completed OK"
                self.logger.info(message)
                return (ResultCode.OK, message)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                  exception_message,
                                                                                  exception_count,
                                                                                  const.ERR_INVOKING_OFF_CMD)

    class EndScanCommand(SKASubarray.EndScanCommand):
        """
        A class for SubarrayNode's EndScan() command.
        """

        def do(self):
            """
            Ends the scan. It is invoked on subarray after completion of the scan duration. It can
            also be invoked by an external client while a scan is in progress, Which stops the scan
            immediately irrespective of the provided scan duration.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: Exception if command execution throws any type of exception
                    DevFailed if the command execution is not successful
            """
            device = self.target
            exception_count = 0
            exception_message = []

            try:
                if device.scan_thread:
                    if device.scan_thread.is_alive():
                        device.scan_thread.cancel()  # stop timer when EndScan command is called
                device.isScanRunning = False
                device.is_scan_completed = True
                # Invoke EndScan command on SDP Subarray Leaf Node
                device._sdp_subarray_ln_proxy.command_inout(const.CMD_END_SCAN)
                self.logger.debug(const.STR_SDP_END_SCAN_INIT)
                device._read_activity_message = const.STR_SDP_END_SCAN_INIT

                # Invoke EndScan command on CSP Subarray Leaf Node
                device._csp_subarray_ln_proxy.command_inout(const.CMD_END_SCAN)
                self.logger.debug(const.STR_CSP_END_SCAN_INIT)
                device._read_activity_message = const.STR_CSP_END_SCAN_INIT
                device._scan_id = ""
                # TODO: For Future Use
                # if device._csp_sa_obs_state == ObsState.IDLE and device._sdp_sa_obs_state ==\
                #         ObsState.IDLE:
                #     if len(device.dishPointingStateMap.values()) != 0:
                #         device.calculate_observation_state()
                device.set_status(const.STR_SCAN_COMPLETE)
                self.logger.info(const.STR_SCAN_COMPLETE)
                device._read_activity_message = const.STR_END_SCAN_SUCCESS
                return (ResultCode.OK, const.STR_END_SCAN_SUCCESS)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_END_SCAN_CMD_ON_GROUP)

            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                                                        exception_message,
                                                                                        exception_count,
                                                                                        const.ERR_END_SCAN_CMD)

            # Throw Exception
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_END_SCAN_EXEC)


    class RestartCommand(SKASubarray.RestartCommand):
        """
        A class for SubarrayNode's Restart() command.
        """

        def do(self):
            """
            This command invokes Restart command on CSPSubarrayLeafNode, SDpSubarrayLeafNode and DishLeafNode.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while invoking command on CSPSubarrayLeafNode, SDpSubarrayLeafNode or
                    DishLeafNode.
                    Exception if error occurs while executing the command.
            """
            device = self.target
            exception_message = []
            exception_count = 0
            try:
                self.logger.info("Restart command invoked on SubarrayNode.")
                # As a part of Restart clear the attributes on SubarrayNode
                device._scan_id = ""
                device._sb_id = ""
                device.scan_duration = 0
                device._scan_type = ''
                # Remove the group for receptors.
                device.remove_receptors_in_group()
                device._sdp_subarray_ln_proxy.command_inout(const.CMD_RESTART)
                self.logger.info(const.STR_CMD_RESTART_INV_SDP)
                device._csp_subarray_ln_proxy.command_inout(const.CMD_RESTART)
                self.logger.info(const.STR_CMD_RESTART_INV_CSP)
                device._dish_leaf_node_group.command_inout(const.CMD_RESTART)
                self.logger.info(const.STR_CMD_RESTART_INV_DISH_GROUP)
                device._read_activity_message = const.STR_RESTART_SUCCESS
                self.logger.info(const.STR_RESTART_SUCCESS)
                device.set_status(const.STR_RESTART_SUCCESS)
                device.is_restart_command = True
                return (ResultCode.STARTED, const.STR_RESTART_SUCCESS)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_RESTART_INVOKING_CMD)
            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                                                        exception_message,
                                                                                        exception_count,
                                                                                        const.ERR_RESTART_INVOKING_CMD)

            # throw exception:
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_RESTART_EXEC)
            # PROTECTED REGION END #    //  SubarrayNode.Restart

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("Track", self.TrackCommand(*args))
        # In order to pass self = subarray node as target device, the assign and release resource commands
        # are registered and inherited from SKASubarray
        self.register_command_object("AssignResources", assign_resources.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseAllResources", release_all_resources.ReleaseAllResourcesCommand(*args))
        self.register_command_object("Configure", configure.ConfigureCommand(*args))
        self.register_command_object("Scan", scan.ScanCommand(*args))


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
