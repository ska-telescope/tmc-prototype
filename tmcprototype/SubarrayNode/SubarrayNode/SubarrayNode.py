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

import os
import sys
import time
import threading
# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SubarrayNode"
sys.path.insert(0, module_path)

import random
import string
from concurrent.futures import ThreadPoolExecutor
import json

# Tango imports
import tango
from tango import DebugIt, DevState, AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run, DeviceMeta, attribute, command, device_property
from future.utils import with_metaclass

# Additional import
import CONST
from CONST import AdminMode, HealthState, ObsMode, ObsState, PointingState
from skabase.SKASubarray.SKASubarray import SKASubarray


__all__ = ["SubarrayNode", "main"]

class SubarrayHealthState:

    @staticmethod
    def generate_health_state_log_msg(health_state, device_name, event):
        if isinstance(health_state, HealthState):
            return (
                CONST.STR_HEALTH_STATE + device_name + CONST.STR_ARROW + health_state.name.upper())
        else:
            return CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(event)

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


class ElementDeviceData:

    @staticmethod
    def build_up_sdp_cmd_data(scan_config, cbf_out_link):
        scan_config = scan_config.copy()
        sdp_scan_config = scan_config.get("sdp", {})

        if sdp_scan_config:
            sdp_config = sdp_scan_config.get("configure")
            if sdp_config:
                scan_config.pop("pointing", None)
                scan_config.pop("dish", None)
                scan_config.pop("csp", None)
                sdp_scan_config["configure"] = sdp_config[0]
                sdp_scan_config["configure"][CONST.STR_CSP_CBFOUTLINK] = cbf_out_link
                cmd_data = tango.DeviceData()
                cmd_data.insert(tango.DevString, json.dumps(scan_config))
            else:
                raise KeyError("SDP Subarray configuration is empty. Command data not built up")
        else:
            raise KeyError("SDP configuration must be given. Aborting SDP configuration.")
        return cmd_data

    @staticmethod
    def build_up_csp_cmd_data(scan_config, scan_id, attr_name_map):
        scan_config = scan_config.copy()
        csp_scan_config = scan_config.get("csp", {})

        if csp_scan_config:
            attr_name_map_keys = list(attr_name_map.keys())
            for key, attribute_name in attr_name_map.items():
                csp_scan_config[key] = attribute_name
            csp_scan_config["pointing"] = scan_config["pointing"]
            csp_scan_config["scanID"] = scan_id
            cmd_data = tango.DeviceData()
            cmd_data.insert(tango.DevString, json.dumps(csp_scan_config))
        else:
            raise KeyError("CSP configuration must be given. Aborting CSP configuration.")
        return cmd_data

    @staticmethod
    def build_up_dsh_cmd_data(scan_config, only_dishconfig_flag):
        scan_config = scan_config.copy()
        if set(["pointing", "dish"]).issubset(scan_config.keys()) or only_dishconfig_flag:
            scan_config.pop("sdp", None)
            scan_config.pop("csp", None)
            cmd_data = tango.DeviceData()
            cmd_data.insert(tango.DevString, json.dumps(scan_config))
        else:
            raise KeyError("Dish configuration must be given. Aborting Dish configuration.")
        return cmd_data


# PROTECTED REGION END #    //  SubarrayNode.additionnal_import


class SubarrayNode(with_metaclass(DeviceMeta, SKASubarray)):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #
    def health_state_cb(self, event):
        """
        Retrieves the subscribed health states, aggregates them
        to calculate the overall subarray health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None
        """
        device_name = event.device.dev_name()
        if not event.err:
            event_health_state = event.attr_value.value
            self.subarray_ln_health_state_map[device_name] = event_health_state

            log_message = SubarrayHealthState.generate_health_state_log_msg(
                event_health_state, device_name, event)
            self._read_activity_message = log_message
            self.logger.debug(log_message)
            self._health_state = SubarrayHealthState.calculate_health_state(
                self.subarray_ln_health_state_map.values())
        else:
            log_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + device_name + str(event)
            self.logger.debug(log_message)
            self._read_activity_message = log_message

    def obsStateCallback(self, evt):
        """
                Retrieves the subscribed CSP_Subarray AND SDP_Subarray  obsState.
                :param evt: A TANGO_CHANGE event on CSP and SDP Subarray obsState.
                :return: None
                """
        exception_message = []
        exception_count = 0
        if evt.err is False:
            try:
                self._observetion_state = evt.attr_value.value

                if CONST.PROP_DEF_VAL_TMCSP_MID_SALN in evt.attr_name:
                    self._csp_sa_obs_state = self._observetion_state
                    self._read_activity_message = CONST.STR_CSP_SUBARRAY_OBS_STATE + str(
                        self._csp_sa_obs_state)
                elif CONST.PROP_DEF_VAL_TMSDP_MID_SALN in evt.attr_name:
                    self._sdp_sa_obs_state = self._observetion_state
                    self._read_activity_message = CONST.STR_SDP_SUBARRAY_OBS_STATE + str(
                        self._sdp_sa_obs_state)
                else:
                    self.logger.debug(CONST.EVT_UNKNOWN)
                    self._read_activity_message = CONST.EVT_UNKNOWN
                self.calculate_observation_state()

            except KeyError as key_error:
                self.logger.error(CONST.ERR_CSPSDP_SUBARRAY_OBS_STATE + str(key_error))
                self._read_activity_message = CONST.ERR_CSPSDP_SUBARRAY_OBS_STATE + str(key_error)
                self.logger.critical(CONST.ERR_CSPSDP_SUBARRAY_OBS_STATE)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                    exception_message, exception_count, CONST.ERR_SUBSR_CSPSDPSA_OBS_STATE)
            except Exception as except_occured:
                [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                exception_message, exception_count, CONST.ERR_AGGR_OBS_STATE)
        else:
            self.logger.debug(CONST.ERR_SUBSR_CSPSDPSA_OBS_STATE + str(evt))
            self._read_activity_message = CONST.ERR_SUBSR_CSPSDPSA_OBS_STATE + str(evt)
            self.logger.critical(CONST.ERR_SUBSR_CSPSDPSA_OBS_STATE)

    def calculate_observation_state(self):
        """
        Calculates aggregated observation state of Subarray.
        """
        pointing_state_count_track = 0
        pointing_state_count_slew = 0
        """can be represented with a function as well"""
        for value in list(self.dishPointingStateMap.values()):
            if value == PointingState.TRACK:
                pointing_state_count_track = pointing_state_count_track + 1
            elif value == PointingState.SLEW:
                pointing_state_count_slew = pointing_state_count_slew + 1
        """several if elif blocks here.. can something be done about it?"""
        if self._csp_sa_obs_state == ObsState.SCANNING and self._sdp_sa_obs_state ==\
                ObsState.SCANNING:
            self._obs_state = ObsState.SCANNING
            # self.isScanning = True
        elif self._csp_sa_obs_state == ObsState.READY and self._sdp_sa_obs_state ==\
                ObsState.READY:
            if pointing_state_count_track == len(self.dishPointingStateMap.values()):
                self._obs_state = ObsState.READY
        elif self._csp_sa_obs_state == ObsState.CONFIGURING or \
                self._sdp_sa_obs_state == ObsState.CONFIGURING:
            self._obs_state = ObsState.CONFIGURING
        elif self._csp_sa_obs_state == ObsState.IDLE and self._sdp_sa_obs_state ==\
                ObsState.IDLE:
            if len(self.dishPointingStateMap.values()) != 0:
                if pointing_state_count_track == len(self.dishPointingStateMap.values()):
                    if self.only_dishconfig_flag == True:
                        if self.isScanning == True:
                            self._obs_state = ObsState.SCANNING
                        else:
                            self._obs_state = ObsState.READY
                    else:
                        self._dish_leaf_node_group.command_inout(CONST.CMD_STOP_TRACK)
                        self._obs_state = ObsState.IDLE
                elif pointing_state_count_slew != 0:
                    self._obs_state = ObsState.CONFIGURING
                else:
                    self._obs_state = ObsState.IDLE

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
            except Exception as ex:
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

    def add_receptors_in_group(self, argin):
        """
        Creates a tango group of the successfully allocated resources in the subarray.
        Device proxy for each of the resources is created. The healthState and pointintgState attributes
        from all the devices in the group are subscribed so that the changes in the respective device are
        received at Subarray Node.


        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVarStringArray. List of receptor IDs to be allocated to subarray.
            Example: ['0001', '0002']

        :return:
            DevVarStringArray. List of Resources added to the Subarray.
            Example: ['0001', '0002']
        """
        exception_count = 0
        exception_message = []
        allocation_success = []
        allocation_failure = []
        # Add each dish into the tango group
        self.logger.debug("add_receptors_in_group::",argin)
        for leafId in range(0, len(argin)):
            try:
                str_leafId = argin[leafId]
                self._dish_leaf_node_group.add(self.DishLeafNodePrefix +  str_leafId)
                devProxy = tango.DeviceProxy(self.DishLeafNodePrefix + str_leafId)
                self._dish_leaf_node_proxy.append(devProxy)
                # Update the list allocation_success with the dishes allocated successfully to subarray
                allocation_success.append(str_leafId)
                # Subscribe Dish Health State
                self._event_id = devProxy.subscribe_event(CONST.EVT_DISH_HEALTH_STATE,
                                                          tango.EventType.CHANGE_EVENT,
                                                          self.health_state_cb,
                                                          stateless=True)
                self._dishLnVsHealthEventID[devProxy] = self._event_id
                self._health_event_id.append(self._event_id)
                self.subarray_ln_health_state_map[devProxy.dev_name()] = HealthState.UNKNOWN
                self.logger.debug(CONST.STR_DISH_LN_VS_HEALTH_EVT_ID +str(self._dishLnVsHealthEventID))

                # Subscribe Dish Pointing State
                self._event_id = devProxy.subscribe_event(CONST.EVT_DISH_POINTING_STATE,
                                                          tango.EventType.CHANGE_EVENT,
                                                          self.setPointingState,
                                                          stateless=True)
                self._dishLnVsPointingStateEventID[devProxy] = self._event_id
                self._pointing_state_event_id.append(self._event_id)
                self.dishPointingStateMap[devProxy] = -1
                self.logger.debug(CONST.STR_DISH_LN_VS_POINTING_STATE_EVT_ID + str(self._dishLnVsPointingStateEventID))
                self._receptor_id_list.append(int(str_leafId))
                self._read_activity_message = CONST.STR_GRP_DEF + str(
                    self._dish_leaf_node_group.get_device_list(True))
                self._read_activity_message = CONST.STR_LN_PROXIES + str(self._dish_leaf_node_proxy)
                self.logger.debug(CONST.STR_SUBS_ATTRS_LN)
                self._read_activity_message = CONST.STR_SUBS_ATTRS_LN
                # TODO: FOR FUTURE REFERENCE
                # self.logger.debug(CONST.STR_HS_EVNT_ID +str(self._health_event_id))
                # self._read_activity_message = CONST.STR_HS_EVNT_ID + str(self._health_event_id)
                # Set state = ON
                self.set_state(DevState.ON)
                # set obsState to "IDLE"
                self._obs_state = ObsState.IDLE
                self.set_status(CONST.STR_ASSIGN_RES_SUCCESS)
                self.logger.info(CONST.STR_ASSIGN_RES_SUCCESS)
            except DevFailed as dev_failed:
                [exception_message, excpt_count] = self._handle_devfailed_exception(dev_failed,
                                                    exception_message, excpt_count, CONST.ERR_ADDING_LEAFNODE)
                allocation_failure.append(str_leafId)
                # Exception Logic to remove Id from subarray group
                group_dishes = self._dish_leaf_node_group.get_device_list()
                if group_dishes.contains(self.DishLeafNodePrefix +  str_leafId):
                    self._dish_leaf_node_group.remove(self.DishLeafNodePrefix + str_leafId)
                # unsubscribe event
                if self._dishLnVsHealthEventID[devProxy]:
                    devProxy.unsubscribe_event(self._dishLnVsHealthEventID[devProxy])

                if self._dishLnVsPointingStateEventID[devProxy]:
                    devProxy.unsubscribe_event(self._dishLnVsPointingStateEventID[devProxy])
            except(DevFailed, Exception) as except_occurred:
                [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, CONST.ERR_ASSIGN_RES_CMD)
        # Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_ASSIGN_RES_EXEC)

        self.logger.debug("add_receptors_in_group::",allocation_success)
        return allocation_success

    def assign_csp_resources(self, argin):
        """
        This function accepts the receptor IDs list as input and invokes the assign resources command on
        the CSP Subarray Leaf Node.

        :param argin: List of strings
            Contains the list of strings that has the resources ids. Currently this list contains only
            receptor ids.

        :return: List of strings.

        Example: ['0001', '0002']

            Returns the list of CSP resources successfully assigned to the Subarray. Currently, the
            CSPSubarrayLeafNode.AssignResources function returns void. The function only loops back
            the input argument in case of successful resource allocation, or returns an empty list in case
            of failure.
        """
        arg_list = []
        json_argument = {}
        argout = []
        dish = {}
        try:
            dish[CONST.STR_KEY_RECEPTOR_ID_LIST] = argin
            json_argument[CONST.STR_KEY_DISH] = dish
            arg_list.append(json.dumps(json_argument))
            self._csp_subarray_ln_proxy.command_inout(CONST.CMD_ASSIGN_RESOURCES, arg_list)
            argout = argin
        except DevFailed as df:
            self.logger.error(CONST.ERR_CSP_CMD)
            self.logger.debug(df)

        # For this PI CSP Subarray Leaf Node does not return anything. So this function is
        # looping the receptor ids back.
        self.logger.debug("assign_csp_resources::",argout)
        return argout

    def assign_sdp_resources(self, argin):
        """
        This function accepts the receptor ID list as input and assigns SDP resources to SDP Subarray
        through SDP Subarray Leaf Node.

        :param argin: List of strings
            Contains the list of strings that has the resources ids. Currently
            processing block ids are passed to this function.

        :return: List of strings.
        Example: ['PB1', 'PB2']

            Returns the list of successfully assigned resources. Currently the
            SDPSubarrayLeafNode.AssignResources function returns void. Thus, this
            function just loops back the input argument in case of success. In case of
            failure, empty list is returned.
        """
        argout = []
        json_argument = {}
        try:
            json_argument[CONST.STR_KEY_PB_ID_LIST] = argin
            str_json_arg = json.dumps(json_argument)
            self._sdp_subarray_ln_proxy.command_inout(CONST.CMD_ASSIGN_RESOURCES, str_json_arg)
            argout = argin
        except DevFailed as df:
            self.logger.error(CONST.ERR_SDP_CMD)
            self.logger.debug(df)

        # For this PI SDP Subarray Leaf Node does not return anything. So this function is
        # looping the processing block ids back.
        self.logger.debug("assign_sdp_resources::",argout)
        return argout

    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(CONST.PROP_DEF_VAL_LEAF_NODE_PREFIX):
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

    def remove_receptors_in_group(self):
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
            self.logger.debug(CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True)))
            self._dish_leaf_node_group.remove_all()
            log_message = CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True))
            self.logger.debug(log_message)
            self._read_activity_message = log_message
        except DevFailed as dev_failed:
            log_message = "Failed to remove receptors from the group. {}".format(dev_failed)
            self.logger.error(log_message)
            self._read_activity_message = log_message
            return

        self.logger.debug(CONST.STR_DISH_PROXY_LIST + str(self._dish_leaf_node_proxy))
        self.logger.debug(CONST.STR_HEALTH_ID + str(self._health_event_id))
        self.logger.debug(CONST.STR_DISH_LN_VS_HEALTH_EVT_ID + str(self._dishLnVsHealthEventID))
        self.logger.debug(CONST.STR_POINTING_STATE_ID + str(self._pointing_state_event_id))
        self.logger.debug(CONST.STR_DISH_LN_VS_POINTING_STATE_EVT_ID +str(self._dishLnVsPointingStateEventID))

        self._unsubscribe_resource_events(self._dishLnVsHealthEventID)
        self._unsubscribe_resource_events(self._dishLnVsPointingStateEventID)

        self._dishLnVsHealthEventID = {}
        self._health_event_id = []
        self._dishLnVsPointingStateEventID = {}
        self._remove_subarray_dish_lns_health_states()
        self.dishPointingStateMap = {}
        self._pointing_state_event_id = []
        self._dish_leaf_node_proxy = []
        self._receptor_id_list = []
        self.set_status(CONST.STR_RECEPTORS_REMOVE_SUCCESS)
        self.logger.info(CONST.STR_RECEPTORS_REMOVE_SUCCESS)

    def release_csp_resources(self):
        """
            This function invokes releaseAllResources command on CSP Subarray via CSP Subarray Leaf
            Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        try:
            self._csp_subarray_ln_proxy.command_inout(CONST.CMD_RELEASE_ALL_RESOURCES)
        except DevFailed as df:
            self.logger.error(CONST.ERR_CSP_CMD)
            self.logger.debug(df)

    def release_sdp_resources(self):
        """
            This function invokes releaseAllResources command on SDP Subarray via SDP Subarray Leaf Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        try:
            self._sdp_subarray_ln_proxy.command_inout(CONST.CMD_RELEASE_ALL_RESOURCES)

        except DevFailed as df:
            self.logger.error(CONST.ERR_SDP_CMD)
            self.logger.debug(df)

    @command(
        dtype_in='str',
        doc_in="Execute Scan on the Subarray",
    )
    @DebugIt()
    def Scan(self, argin):
        """
        This command accepts time interval as input. And it Schedule scan on subarray
        from where scan command is invoked on respective CSP and SDP subarray node for the
        provided interval of time. It checks whether the scan is already in progress. If yes it
        throws error showing duplication of command.

        :param argin: DevVarStringArray. JSON string containing scan duration.

        JSON string example as follows:

        {"scanDuration": 10.0}

        Note: Above JSON string can be used as an input argument while invoking this command from JIVE.

        :return: None
        """
        exception_count = 0
        exception_message = []
        try:
            json_scan_duration = json.loads(argin)
            self.scan_duration = int(json_scan_duration['scanDuration'])
            self.logger.debug(CONST.STR_SCAN_IP_ARG, argin)
            assert self._obs_state != ObsState.SCANNING, CONST.SCAN_ALREADY_IN_PROGRESS
            if self._obs_state == ObsState.READY:
                self._read_activity_message = CONST.STR_SCAN_IP_ARG + argin
                self.isScanning = True
                # Invoke Scan command on SDP Subarray Leaf Node
                cmdData = tango.DeviceData()
                cmdData.insert(tango.DevString, argin)
                self._sdp_subarray_ln_proxy.command_inout(CONST.CMD_SCAN, cmdData)
                self.logger.debug(CONST.STR_SDP_SCAN_INIT)
                self._read_activity_message = CONST.STR_SDP_SCAN_INIT

                # Invoke Scan command on CSP Subarray Leaf Node
                csp_argin = []
                csp_argin.append(argin)
                cmdData = tango.DeviceData()
                cmdData.insert(tango.DevVarStringArray, csp_argin)
                self._csp_subarray_ln_proxy.command_inout(CONST.CMD_START_SCAN, cmdData)
                self.logger.debug(CONST.STR_CSP_SCAN_INIT)
                self._read_activity_message = CONST.STR_CSP_SCAN_INIT

                if self._csp_sa_obs_state == ObsState.IDLE and self._sdp_sa_obs_state ==\
                        ObsState.IDLE:
                    if len(self.dishPointingStateMap.values()) != 0:
                        self.calculate_observation_state()

                self.set_status(CONST.STR_SA_SCANNING)
                self.logger.info(CONST.STR_SA_SCANNING)
                self._read_activity_message = CONST.STR_SCAN_SUCCESS

            self.end_scan_thread = threading.Thread(None, self.waitForEndScan, "SubarrayNode")
            self.end_scan_thread.start()
            # TODO: FOR FUTURE IMPLEMENTATION
            # with excpt_count is 0 and ThreadPoolExecutor(1) as executor:
            #     status = executor.submit(self.waitForEndScan, scan_duration)
            #     if status:
            #         # call endScan command
            #         self.logger.debug("Sending end scan command...")
            #         self.EndScan()

            #TODO: FOR FUTURE IMPLEMENTATION
            # if type(float(argin[0])) == float:
            #     self.logger.debug("Observation state:", self._obs_state)
            #     assert self._obs_state != ObsState.SCANNING, CONST.SCAN_ALREADY_IN_PROGRESS
            #     self.logger.debug(CONST.STR_GRP_DEF +str(self._dish_leaf_node_group.get_device_list()))
            #     self._read_activity_message = CONST.STR_SCAN_IP_ARG + str(argin)
            #     self._read_activity_message = CONST.STR_GRP_DEF + str(
            #         self._dish_leaf_node_group.get_device_list())
            #     cmdData = tango.DeviceData()
            #     cmdData.insert(tango.DevString, argin[0])
            #     self._dish_leaf_node_group.command_inout(CONST.CMD_SCAN, cmdData)
            #     # set obsState to SCANNING when the scan is started
            #     self._obs_state = ObsState.SCANNING
            #     self.set_status(CONST.STR_SA_SCANNING)
            #     self.logger.info(CONST.STR_SA_SCANNING)
        except AssertionError as assert_error:
            str_log = CONST.ERR_SCAN_CMD + "\n" +str(assert_error) + CONST.ERR_DUPLICATE_SCAN_CMD
            self.logger.error(str_log)
            self._read_activity_message = CONST.ERR_DUPLICATE_SCAN_CMD + str(assert_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except ValueError as value_error:
            str_log = CONST.ERR_SCAN_CMD + str(value_error) + CONST.ERR_INVALID_DATATYPE
            self.logger.error(str_log)
            self._read_activity_message = CONST.ERR_INVALID_DATATYPE + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except KeyError as key_err:
            self.logger.error(CONST.ERR_SCAN_CMD + str(key_err))
            self._read_activity_message = CONST.ERR_SCAN_CMD + str(key_err)
            self.logger.error(CONST.ERR_SCAN_CMD)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                                    exception_message, exception_count, CONST.ERR_SCAN_CMD)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                    exception_message, exception_count, CONST.ERR_SCAN_CMD)
        #Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_SCAN_EXEC)
            # err_msg = ' '
            # for item in excpt_msg:
            #     err_msg += str(item) + "\n"
            # tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
            #                              CONST.STR_SCAN_EXEC, tango.ErrSeverity.ERR)

    def waitForEndScan(self):
        scanning_time = 0.0
        while scanning_time <= self.scan_duration:
            # Stop thread, if EndScan command is invoked manually
            if self._endscan_stop == True:
                break
            # Stop thread, if scan duration is commpleted and EndScan is not invoked manually.
            elif self._endscan_stop == False and scanning_time == self.scan_duration:
                self.EndScan()
                break
            # Increment counter till maximum scan duration provided with scan command
            else:
                time.sleep(1)
                scanning_time += 1
        self._endscan_stop = False

    def is_Scan_allowed(self):
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
    @command(
    )
    @DebugIt()
    def EndScan(self):
        """ Ends the scan. It is invoked on subarray after completion of the scan duration. It can
        also be invoked by an external client while a scan is in progress, Which stops the scan
        immediately irrespective of the provided scan duration.

        :param argin: DevVoid.

        :return: None
        """
        exception_count = 0
        exception_message = []
        self._endscan_stop = True
        try:
            assert self._obs_state == ObsState.SCANNING, CONST.SCAN_ALREADY_COMPLETED
            if self._obs_state == ObsState.SCANNING:
                self.isScanning = False
                # Invoke EndScan command on SDP Subarray Leaf Node
                self._sdp_subarray_ln_proxy.command_inout(CONST.CMD_END_SCAN)
                self.logger.debug(CONST.STR_SDP_END_SCAN_INIT)
                self._read_activity_message = CONST.STR_SDP_END_SCAN_INIT

                # Invoke EndScan command on CSP Subarray Leaf Node
                self._csp_subarray_ln_proxy.command_inout(CONST.CMD_END_SCAN)
                self.logger.debug(CONST.STR_CSP_END_SCAN_INIT)
                self._read_activity_message = CONST.STR_CSP_END_SCAN_INIT
                self._scan_id = ""

                if self._csp_sa_obs_state == ObsState.IDLE and self._sdp_sa_obs_state ==\
                        ObsState.IDLE:
                    if len(self.dishPointingStateMap.values()) != 0:
                        self.calculate_observation_state()

                self.set_status(CONST.STR_SCAN_COMPLETE)
                self.logger.info(CONST.STR_SCAN_COMPLETE)
                self._read_activity_message = CONST.STR_END_SCAN_SUCCESS

                # TODO: FOR FUTURE IMPLEMENTATION
                # cmdData = tango.DeviceData()
                # cmdData.insert(tango.DevString, "0")
                # self._dish_leaf_node_group.command_inout(CONST.CMD_END_SCAN, cmdData)
                # set obsState to READY when the scan is ended
                # self._obs_state = ObsState.READY
                # self._scan_id = ""
                # self.set_status(CONST.STR_SCAN_COMPLETE)
                # self.logger.info(CONST.STR_SCAN_COMPLETE)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count, CONST.ERR_END_SCAN_CMD_ON_GROUP)
        except AssertionError as assert_err:
            str_log = CONST.ERR_DUPLICATE_END_SCAN_CMD + "\n" + str(assert_err)
            self.logger.error(str_log)
            self._read_activity_message = CONST.ERR_DUPLICATE_END_SCAN_CMD
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, CONST.ERR_END_SCAN_CMD)
        # Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_END_SCAN_EXEC)

    def is_EndScan_allowed(self):
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    @command(
        dtype_in=('str',),
        doc_in="List of Resources to add to subarray.",
        dtype_out=('str',),
        doc_out="A list of Resources added to the subarray.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        Assigns resources to the subarray. It accepts receptor id list as an array of
        DevStrings. Upon successful execution, the 'receptorIDList' attribute of the
        subarray is updated with the list of receptors, and returns list of assigned
        resources as array of DevStrings.

        Note: Resource allocation for CSP and SDP resources is also implemented but
        currently CSP accepts only receptorIDList and SDP accepts only dummy resources.

        :param argin:
            DevVarStringArray. List of receptor IDs to be allocated to subarray.

            Example: ['0001', '0002'] as argin

        :return:
            DevVarStringArray. List of Resources added to the Subarray.

            Example: ['0001', '0002'] as argout if allocation successful

                [] as argout if allocation unsuccessful
        """
        exception_count = 0
        exception_message = []

        # 1. Argument validation
        try:
            # Allocation success and failure lists
            for leafId in range(0, len(argin)):
                float(argin[leafId])
                self.logger.debug("assign_resource_argin",argin)
        except ValueError as value_error:
            str_log = CONST.ERR_SCAN_CMD +"\n" + str(value_error) + CONST.ERR_INVALID_DATATYPE
            self.logger.error(str_log)
            self.logger.error(CONST.ERR_INVALID_DATATYPE)
            self._read_activity_message = CONST.ERR_INVALID_DATATYPE + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        with exception_count is 0 and ThreadPoolExecutor(3) as executor:
            # 2.1 Create group of receptors
            self.logger.info(CONST.STR_DISH_ALLOCATION)
            dish_allocation_status = executor.submit(self.add_receptors_in_group, argin)

            # 2.2. Add resources in CSP subarray
            self.logger.info(CONST.STR_CSP_ALLOCATION)
            csp_allocation_status = executor.submit(self.assign_csp_resources, argin)

            # 2.3. Add resources in SDP subarray
            # For PI#3, TMC sends dummy resources to SDP.
            self.logger.info(CONST.STR_SDP_ALLOCATION)
            dummy_sdp_resources = ["PB1", "PB2"]
            sdp_allocation_status = executor.submit(self.assign_sdp_resources, dummy_sdp_resources)

            # 2.4 wait for result
            while (dish_allocation_status.done() is False or
                   csp_allocation_status.done() is False or
                   sdp_allocation_status.done() is False
                  ):
                pass

            # 2.5. prepare return value
            dish_allocation_result = dish_allocation_status.result()
            log_msg = CONST.STR_DISH_ALLOCATION_RESULT + str(dish_allocation_result)
            self.logger.debug(log_msg)

            csp_allocation_result = csp_allocation_status.result()
            log_msg = CONST.STR_CSP_ALLOCATION_RESULT + str(csp_allocation_result)
            self.logger.debug(log_msg)

            sdp_allocation_result = sdp_allocation_status.result()
            log_msg = CONST.STR_SDP_ALLOCATION_RESULT + str(sdp_allocation_result)
            self.logger.debug(log_msg)

            dish_allocation_result.sort()
            csp_allocation_result.sort()
            sdp_allocation_result.sort()
            argin.sort()
            dummy_sdp_resources.sort()

            if(dish_allocation_result == argin and
                csp_allocation_result == argin and
                sdp_allocation_result == dummy_sdp_resources
              ):
                # Currently sending only dish allocation results.
                argout = dish_allocation_result
            else:
                #TODO: Need to add code to revert allocated resources
                argout = []
        # return dish_allocation_result
        self.logger.debug("assign_resource_argout",argout)
        return argout

    def is_AssignResources_allowed(self):
        """Checks if AssignResources is allowed in the current state of SubarrayNode."""
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    @command(
        dtype_out=('str',),
        doc_out="List of resources removed from the subarray.",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        """
        It checks whether all resources are already released. If yes then it throws error while
        executing command. If not it Releases all the resources from the subarray i.e. Releases
        resources from TMC Subarray Node, CSP Subarray and SDP Subarray. If the command
        execution fails, array of receptors(device names) which are failed to be released from the
        subarray, is returned to Central Node. Upon successful execution, all the resources of a given
        subarray get released and empty array is returned. Selective release is not yet supported.

        :param argin: DevVoid.

        :return: DevVarStringArray.
        Example: "[]" as argout on successful release all resources.
        """
        try:
            assert self._dishLnVsHealthEventID != {}, CONST.RESRC_ALREADY_RELEASED
        except AssertionError as assert_err:
            log_message = CONST.ERR_RELEASE_RES_CMD + str(assert_err)
            self.logger.error(log_message)
            self._read_activity_message = log_message
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, log_message,
                                         CONST.STR_RELEASE_ALL_RES_EXEC, tango.ErrSeverity.ERR)

        self.logger.info(CONST.STR_DISH_RELEASE)
        self.remove_receptors_in_group()
        self.logger.info(CONST.STR_CSP_RELEASE)
        self.release_csp_resources()
        self.logger.info(CONST.STR_SDP_RELEASE)
        self.release_sdp_resources()


        self._scan_id = ""
        # For now cleared SB ID in ReleaseAllResources command. When the EndSB command is implemented,
        # It will be moved to that command.
        self._sb_id = ""
        self.set_state(DevState.OFF)
        self._obs_state = ObsState.IDLE

        argout = self._dish_leaf_node_group.get_device_list(True)

        self.logger.debug("Release_all_resources:",argout)
        return argout

    def is_ReleaseAllResources_allowed(self):
        """Checks if ReleaseAllResources is allowed in the current state of SubarrayNode."""
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    def setPointingState(self, evt):
        """
        Retrieves the subscribed DishMaster health state, aggregate them to evaluate
        health state of the Subarray.

        :param evt: A TANGO_CHANGE event on DishMaster healthState.

        :return: None

        """
        if evt.err is False:
            try:
                self._dish_pointing_state = evt.attr_value.value
                self.dishPointingStateMap[evt.device] = self._dish_pointing_state
                if self._dish_pointing_state == PointingState.READY:
                    str_log = CONST.STR_POINTING_STATE + str(evt.device) + CONST.STR_READY
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                elif self._dish_pointing_state == PointingState.SLEW:
                    str_log = CONST.STR_POINTING_STATE + str(evt.device) + CONST.STR_SLEW
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                elif self._dish_pointing_state == PointingState.TRACK:
                    str_log = CONST.STR_POINTING_STATE + str(evt.device) + CONST.STR_TRACK
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                elif self._dish_pointing_state == PointingState.SCAN:
                    str_log = CONST.STR_POINTING_STATE + str(evt.device) + CONST.STR_SCAN
                    self.logger.debug(str_log)
                    self._read_activity_message = str_log
                else:
                    self.logger.debug(CONST.STR_HEALTH_STATE_UNKNOWN_VAL, evt)
                    self._read_activity_message = CONST.STR_POINTING_STATE_UNKNOWN_VAL + str(evt)
                self.calculate_observation_state()
            except KeyError as key_err:
                self.logger.error(CONST.ERR_SETPOINTING_CALLBK + str(key_err))
                self._read_activity_message = CONST.ERR_SETPOINTING_CALLBK + str(key_err)
            except Exception as except_occurred:
                self.logger.error(CONST.ERR_AGGR_POINTING_STATE + str(except_occurred.message))
                self._read_activity_message = CONST.ERR_AGGR_POINTING_STATE + str(except_occurred.message)
        else:
            self.logger.debug(CONST.ERR_SUBSR_DSH_POINTING_STATE + str(evt.errors))
            self._read_activity_message = CONST.ERR_SUBSR_DSH_POINTING_STATE + str(evt.errors)

    def _handle_generic_exception(self, exception, excpt_msg_list, exception_count, read_actvity_msg):
        self.logger.error(read_actvity_msg + str(exception))
        self._read_activity_message = read_actvity_msg + str(exception)
        excpt_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [excpt_msg_list, exception_count]

    def _handle_devfailed_exception(self, df, excpt_msg_list, exception_count, read_actvity_msg):
        self.logger.error(read_actvity_msg + str(df))
        self._read_activity_message = read_actvity_msg + str(df)
        excpt_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [excpt_msg_list, exception_count]

    def throw_exception(self, excpt_msg_list, read_actvity_msg):
        err_msg = ''
        for item in excpt_msg_list:
            err_msg += item + "\n"
        tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)
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

    def init_device(self):
        """
        Initializes the attributes and properties of the Subarray node.

        :return: None
        """
        SKASubarray.init_device(self)
        # PROTECTED REGION ID(SubarrayNode.init_device) ENABLED START #
        self.set_state(DevState.INIT)
        self.set_status(CONST.STR_SA_INIT)
        self.SkaLevel = 2  # set SKALevel to "2"
        self._admin_mode = AdminMode.OFFLINE
        self._health_state = HealthState.OK
        self._obs_state = ObsState.IDLE
        self._obs_mode = ObsMode.IDLE
        self._simulation_mode = False
        self.isScanning = False
        self._scan_id = ""
        self._sb_id = ""
        self._receptor_id_list = []
        self.dishPointingStateMap = {}
        self._dish_leaf_node_group = tango.Group(CONST.GRP_DISH_LEAF_NODE)
        self._dish_leaf_node_proxy = []
        self._health_event_id = []
        self._pointing_state_event_id = []
        self._dishLnVsHealthEventID = {}
        self._dishLnVsPointingStateEventID = {}
        self.subarray_ln_health_state_map = {}
        self._subarray_health_state = HealthState.OK  #Aggregated Subarray Health State
        self._csp_sa_obs_state = ObsState.IDLE
        self._sdp_sa_obs_state = ObsState.IDLE
        self.only_dishconfig_flag = False
        self._endscan_stop = False
        _state_fault_flag = False    # flag use to check whether state set to fault if exception occurs.


        # Create proxy for CSP Subarray Leaf Node
        self._csp_subarray_ln_proxy = None
        result = self.create_csp_ln_proxy()
        # Create proxy for SDP Subarray Leaf Node
        self._sdp_subarray_ln_proxy = None
        result = self.create_sdp_ln_proxy()
        try:
            self.subarray_ln_health_state_map[self._csp_subarray_ln_proxy.dev_name()] = (
                HealthState.UNKNOWN)
            # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
            self._csp_subarray_ln_proxy.subscribe_event(
                CONST.EVT_CSPSA_HEALTH, EventType.CHANGE_EVENT,self.health_state_cb,
                stateless=True)
            # Subscribe cspSubarrayObsState (forwarded attribute) of CspSubarray
            self._csp_subarray_ln_proxy.subscribe_event(CONST.EVT_CSPSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                        self.obsStateCallback, stateless=True)

            self.set_status(CONST.STR_CSP_SA_LEAF_INIT_SUCCESS)
            self.logger.info(CONST.STR_CSP_SA_LEAF_INIT_SUCCESS)
        except DevFailed as dev_failed:
            self.logger.error(CONST.ERR_SUBS_CSP_SA_LEAF_ATTR + str(dev_failed))
            self._read_activity_message = CONST.ERR_SUBS_CSP_SA_LEAF_ATTR + str(dev_failed)
            self.set_state(DevState.FAULT)
            _state_fault_flag = True
            self.set_status(CONST.ERR_SUBS_CSP_SA_LEAF_ATTR)
            self.logger.error(CONST.ERR_CSP_SA_LEAF_INIT)

        try:
            self.subarray_ln_health_state_map[self._sdp_subarray_ln_proxy.dev_name()] = (
                HealthState.UNKNOWN)
            # Subscribe sdpSubarrayHealthState (forwarded attribute) of SdpSubarray
            self._sdp_subarray_ln_proxy.subscribe_event(CONST.EVT_SDPSA_HEALTH, EventType.CHANGE_EVENT,
                                                        self.health_state_cb, stateless=True)
            # Subscribe sdpSubarrayObsState (forwarded attribute) of SdpSubarray
            self._sdp_subarray_ln_proxy.subscribe_event(CONST.EVT_SDPSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                        self.obsStateCallback, stateless=True)
            self.set_status(CONST.STR_SDP_SA_LEAF_INIT_SUCCESS)
        except DevFailed as dev_failed:
            self.logger.error(CONST.ERR_SUBS_SDP_SA_LEAF_ATTR + str(dev_failed))
            self._read_activity_message = CONST.ERR_SUBS_SDP_SA_LEAF_ATTR + str(dev_failed)
            self.set_state(DevState.FAULT)
            _state_fault_flag = True
            self.set_status(CONST.ERR_SUBS_SDP_SA_LEAF_ATTR)

        self._read_activity_message = CONST.STR_SA_INIT_SUCCESS
        self.set_status(CONST.STR_SA_INIT_SUCCESS)
        self.logger.info(CONST.STR_SA_INIT_SUCCESS)

        if(_state_fault_flag == True):
            self.set_state(DevState.FAULT)           # Set state = FAULT
        else:
            self.set_state(DevState.DISABLE)         # Set state = DISABLE

        # PROTECTED REGION END #    //  SubarrayNode.init_device


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
        self.logger.debug("read_scanID",self._scan_id)
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
    def _configure_leaf_node(self, device_proxy, cmd_name, cmd_data):
        try:
            device_proxy.command_inout(cmd_name, cmd_data)
            self.logger.debug("{} configured succesfully.".format(device_proxy.dev_name()))
        except DevFailed as df:
            log_message = df[0].desc
            self._read_activity_message = log_message
            self.logger.error("Failed to configure {}. {}".format(device_proxy.dev_name(), df))
            raise

    def _create_cmd_data(self, method_name, scan_config, *args):
        try:
            method = getattr(ElementDeviceData, method_name)
            cmd_data = method(scan_config, *args)
        except KeyError as kerr:
            log_message = kerr.args[0]
            self._read_activity_message = log_message
            self.logger.debug(log_message)
            raise
        return cmd_data

    def _configure_sdp(self, scan_configuration):
        cbf_out_link = self.CspSubarrayFQDN + "/cbfOutputLink"
        cmd_data = self._create_cmd_data("build_up_sdp_cmd_data", scan_configuration, cbf_out_link)
        self._configure_leaf_node(self._sdp_subarray_ln_proxy, "Configure", cmd_data)

    def _configure_csp(self, scan_configuration):
        attr_name_map = {
            CONST.STR_DELAY_MODEL_SUB_POINT: self.CspSubarrayLNFQDN + "/delayModel",
            CONST.STR_VIS_DESTIN_ADDR_SUB_POINT: self.SdpSubarrayFQDN + "/receiveAddresses"
        }

        cmd_data = self._create_cmd_data(
            "build_up_csp_cmd_data", scan_configuration, self._scan_id, attr_name_map)
        self._configure_leaf_node(self._csp_subarray_ln_proxy, "ConfigureScan", cmd_data)

    def _configure_dsh(self, scan_configuration, argin):
        config_keys = scan_configuration.keys()
        if not set(["sdp", "csp"]).issubset(config_keys) and "dish" in config_keys:
            self.only_dishconfig_flag = True

        cmd_data = self._create_cmd_data(
            "build_up_dsh_cmd_data", scan_configuration, self.only_dishconfig_flag)

        try:
            self._dish_leaf_node_group.command_inout(CONST.CMD_CONFIGURE, cmd_data)
            self._dish_leaf_node_group.command_inout(CONST.CMD_TRACK, cmd_data)
        except DevFailed as df:
            self._read_activity_message = df[0].desc
            self.logger.error(df)
            raise

    @command(
        dtype_in='str',
        doc_in="Pointing parameters of Dish - Right ascension and Declination coordinates.",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SubarrayNode.Configure) ENABLED START #
        """
        Configures the resources assigned to the Subarray.The configuration data for SDP, CSP and Dish is
        extracted out of the input configuration string and relayed to the respective underlying devices (SDP
        Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node).

        :param argin: DevString.
        JSON string that includes pointing parameters of Dish - Azimuth and Elevation Angle, CSP
        Configuration and SDP Configuration parameters.

        JSON string example is:

        {"scanID":123,"pointing":{"target":{"system":"ICRS","name":"Polaris","RA":"02:31:49.0946","dec":
        "+89:15:50.7923"}},"dish":{"receiverBand":"1"},"csp":{"frequencyBand":"1","fsp":[{"fspID":1,"functionMode"
        :"CORR","frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0}]},"sdp":{"configure":[{"id":
        "realtime-20190627-0001","sbiId":"20190627-0001","workflow":{"id":"vis_ingest","type":"realtime","version"
        :"0.1.0"},"parameters":{"numStations":4,"numChannels":372,"numPolarisations":4,"freqStartHz":0.35e9,
        "freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"Polaris","ra":0.662432049839445,"dec":
        1.5579526053855042}}},"scanParameters":{"123":{"fieldId":0,"intervalMs":1400}}}]}}

        Note: While invoking this command from JIVE, provide above JSON string without any space.

        :return: None
        """
        self.logger.info(CONST.STR_CONFIGURE_CMD_INVOKED_SA)
        self.logger.info(CONST.STR_CONFIGURE_IP_ARG + str(argin))
        self.set_status(CONST.STR_CONFIGURE_CMD_INVOKED_SA)
        self._read_activity_message = CONST.STR_CONFIGURE_CMD_INVOKED_SA

        if self._obs_state != ObsState.IDLE:
            return

        try:
            scan_configuration = json.loads(argin)
        except json.JSONDecodeError as jerror:
            log_message = CONST.ERR_INVALID_JSON + str(jerror)
            self.logger.error(log_message)
            self._read_activity_message = log_message
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, log_message,
                                         CONST.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)

        if "scanID" not in scan_configuration:
            log_message = "'scanID' must be given. Aborting configuration."
            self.logger.error(log_message)
            self._read_activity_message = log_message
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, log_message,
                                         CONST.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)

        self._scan_id = str(scan_configuration["scanID"])
        self._sb_id = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                                for _ in range(4))

        self._configure_csp(scan_configuration)
        # Reason for the sleep: https://gitlab.com/ska-telescope/tmc-prototype/-/merge_requests/29/diffs#note_284094726
        time.sleep(2)
        self._configure_sdp(scan_configuration)
        self._configure_dsh(scan_configuration, argin)
        ## PROTECTED REGION END #    //  SubarrayNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(SubarrayNode.is_Configure_allowed) ENABLED START #
        """ Checks if the Configure command is allowed in the current state of the Subarray. """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
        # PROTECTED REGION END #    //  SubarrayNode.is_Configure_allowed

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(SubarrayNode.EndSB) ENABLED START #
        """
        This command on Subarray Node invokes EndSB command on CSP Subarray Leaf Node and SDP
        Subarray Leaf Node, and stops tracking of all the assigned dishes.

        :return: None.
        """
        exception_message = []
        exception_count = 0
        try:
            self.logger.debug("EndSB invoked on SubarrayNode.")
            if self._obs_state == ObsState.READY:
                self._sdp_subarray_ln_proxy.command_inout(CONST.CMD_ENDSB)
                self._csp_subarray_ln_proxy.command_inout(CONST.CMD_ENDSB)
                self._dish_leaf_node_group.command_inout(CONST.CMD_STOP_TRACK)
                self._read_activity_message = CONST.STR_ENDSB_SUCCESS
                self.logger.info(CONST.STR_ENDSB_SUCCESS)
                self.set_status(CONST.STR_ENDSB_SUCCESS)
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_READY
                self.logger.error(CONST.ERR_DEVICE_NOT_READY)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_ENDSB_INVOKING_CMD)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, CONST.ERR_ENDSB_INVOKING_CMD)
        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_ENDSB_EXEC)
        # PROTECTED REGION END #    //  SubarrayNode.EndSB

    @command(
        dtype_in='str',
        doc_in="Initial Pointing parameters of Dish - Right Ascension and Declination coordinates.",
    )
    @DebugIt()
    def Track(self, argin):
        # PROTECTED REGION ID(SubarrayNode.Track) ENABLED START #
        """ Invokes Track command on the Dishes assigned to the Subarray.

        :param argin: DevString

        Example:
        radec|2:31:50.91|89:15:51.4 as argin
        Argin to be provided is the Ra and Dec values in the following format: radec|2:31:50.91|89:15:51.4
        Where first value is tag that is radec, second value is Ra in Hr:Min:Sec, and third value is Dec in
        Deg:Min:Sec.

        :return: None

        """
        exception_message= []
        exception_count = 0
        self.logger.debug("Track:",argin)
        try:
            self._read_activity_message = CONST.STR_TRACK_IP_ARG + argin
            # set obsState to CONFIGURING when the configuration is started
            # self._obs_state = ObsState.CONFIGURING
            cmd_input = []
            cmd_input.append(argin)
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevVarStringArray, cmd_input)
            self._dish_leaf_node_group.command_inout(CONST.CMD_TRACK, cmdData)
            # set obsState to READY when the configuration is completed
            # self._obs_state = ObsState.READY
            self._scan_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            #self._sb_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self.logger.info(CONST.STR_TRACK_CMD_INVOKED_SA)

        except tango.DevFailed as devfailed:
            exception_message.append(CONST.ERR_TRACK_CMD + ": " + \
                           str(devfailed.args[0].desc))
            exception_count += 1
        except Exception as except_occured:
            str_log = CONST.ERR_TRACK_CMD + "\n" + str(except_occured)
            self.logger.error(str_log)
            self._read_activity_message = CONST.ERR_TRACK_CMD + str(except_occured)
            self.logger.error(CONST.ERR_TRACK_CMD)
            exception_message.append(CONST.ERR_TRACK_CMD + ": " + \
                             str(except_occured.args[0].desc))
            exception_count += 1

        # throw exception
        if exception_count > 0:
            err_msg = ' '
            for item in exception_message:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_TRACK_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  SubarrayNode.Track
    @command(
    )
    @DebugIt()
    def On(self):
        """
        Changes the admin_mode from offline to online and dev_state from disabled to off.
        :return: None
        """
        # PROTECTED REGION ID(SubarrayNode.StartUp) ENABLED START #
        self._admin_mode = AdminMode.ONLINE
        self.set_state(DevState.OFF)       # Set state = OFF
        # PROTECTED REGION END #    //  SubarrayNode.StartUp

    @command(
    )
    @DebugIt()
    def Standby(self):
        """
        Changes the admin_mode from online to offline and dev_state from  off to disabled.
        :return: None
        """
        # PROTECTED REGION ID(SubarrayNode.Standby) ENABLED START #
        self._admin_mode = AdminMode.OFFLINE
        self.set_state(DevState.DISABLE)  # Set state = DISABLED
        # PROTECTED REGION END #    //  SubarrayNode.Standby
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
