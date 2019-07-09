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
import random
import string
# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #

from concurrent.futures import ThreadPoolExecutor
import threading
import json

# Tango imports
import tango
from tango import DebugIt, DevState, AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run, DeviceMeta, attribute, command, device_property
from future.utils import with_metaclass
from skabase.SKASubarray.SKASubarray import SKASubarray

# Additional import
import CONST


file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SubarrayNode"
sys.path.insert(0, module_path)

# PROTECTED REGION END #    //  SubarrayNode.additionnal_import

__all__ = ["SubarrayNode", "main"]

class SubarrayNode(with_metaclass(DeviceMeta, SKASubarray)):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #

    def sa_healthStateCallback(self, evt):
        """
        Retrieves the subscribed CSP_Subarray health state, aggregates them to calculate the
        subarray health state.
        :param evt: A TANGO_CHANGE event on CSP_Subarray healthState.
        :return: None
        """
        if evt.err is False:
            try:
                self._health_state = evt.attr_value.value
                if CONST.PROP_DEF_VAL_TMCSP_MID_SALN in evt.attr_name:
                    self._csp_sa = self._health_state
                else:
                    print(CONST.EVT_UNKNOWN)
                    self._read_activity_message = CONST.EVT_UNKNOWN

                self.csp_subarray_ln_health_state_map[evt.device] = self._health_state

                if self._health_state == CONST.ENUM_OK:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_OK)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                                                                               ) + CONST.STR_OK
                elif self._health_state == CONST.ENUM_DEGRADED:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_DEGRADED)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                                                                               ) + CONST.STR_DEGRADED
                elif self._health_state == CONST.ENUM_UNKNOWN:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_UNKNOWN)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(
                        evt.device) + CONST.STR_UNKNOWN
                else:
                    print(CONST.STR_HEALTH_STATE_UNKNOWN_VAL, evt)
                    self._read_activity_message = CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(evt)

                # Aggregated Health State
                failed_health_count = 0
                degraded_health_count = 0
                unknown_health_count = 0
                ok_health_count = 0
                # Check the health state of Csp Master Leaf Node
                for value in list(self.csp_subarray_ln_health_state_map.values()):
                    if value == CONST.ENUM_FAILED:
                        failed_health_count = failed_health_count + 1
                        break
                    elif value == CONST.ENUM_DEGRADED:
                        degraded_health_count = degraded_health_count + 1
                    elif value == CONST.ENUM_UNKNOWN:
                        unknown_health_count = unknown_health_count + 1
                    else:
                        ok_health_count = ok_health_count + 1

                    if ok_health_count == len(list(self.csp_subarray_ln_health_state_map.values())) + 1:
                        self._subarray_health_state = CONST.ENUM_OK
                    elif failed_health_count != 0:
                        self._subarray_health_state = CONST.ENUM_FAILED
                    elif degraded_health_count != 0:
                        self._subarray_health_state = CONST.ENUM_DEGRADED
                    else:
                        self._subarray_health_state = CONST.ENUM_UNKNOWN

            except KeyError as key_error:
                print(CONST.ERR_CSP_SUBARRAY_HEALTHSTATE, key_error)
                self._read_activity_message = CONST.ERR_CSP_SUBARRAY_HEALTHSTATE + str(key_error)
                self.dev_logging(CONST.ERR_CSP_SUBARRAY_HEALTHSTATE, int(tango.LogLevel.LOG_FATAL))
            except DevFailed as dev_failed:
                print(CONST.ERR_SUBSR_CSPSA_HEALTH_STATE, dev_failed)
                self._read_activity_message = CONST.ERR_SUBSR_CSPSA_HEALTH_STATE + str(dev_failed)
                self.dev_logging(CONST.ERR_SUBSR_CSPSA_HEALTH_STATE, int(tango.LogLevel.LOG_FATAL))
            except Exception as except_occured:
                print(CONST.ERR_AGGR_HEALTH_STATE, except_occured)
                self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(except_occured)
                self.dev_logging(CONST.ERR_AGGR_HEALTH_STATE, int(tango.LogLevel.LOG_FATAL))
        else:
            print(CONST.ERR_SUBSR_CSPSA_HEALTH_STATE, evt)
            self._read_activity_message = CONST.ERR_SUBSR_CSPSA_HEALTH_STATE + str(evt)
            self.dev_logging(CONST.ERR_SUBSR_CSPSA_HEALTH_STATE, int(tango.LogLevel.LOG_FATAL))



    def cspsubarrayHealthCallback(self, evt):
        """
        Retrieves the subscribed cspsubarrayHealthState attribute of CSPSubarray.

        :param evt: A TANGO_CHANGE event on cspsubarrayHealthState attribute.

        :return: None
        """
        if evt.err is False:
            try:
                self._csp_sa_health = evt.attr_value.value
                if self._csp_sa_health == 0:
                    print(CONST.STR_CSP_SA_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_SA_HEALTH_OK
                elif self._csp_sa_health == 1:
                    print(CONST.STR_CSP_SA_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_SA_HEALTH_DEGRADED
                elif self._csp_sa_health == 2:
                    print(CONST.STR_CSP_SA_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_SA_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_SA_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_SA_HEALTH_UNKNOWN
            except DevFailed as dev_failed:
                print(CONST.ERR_ON_SUBS_CSP_SA_HEALTH, dev_failed)
                self._read_activity_message = CONST.ERR_ON_SUBS_CSP_SA_HEALTH + str(dev_failed)
                self.dev_logging(CONST.ERR_ON_SUBS_CSP_SA_HEALTH, int(tango.LogLevel.LOG_FATAL))
            except Exception as except_occurred:
                print(CONST.ERR_CSP_CBF_HEALTH_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_CSP_CBF_HEALTH_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_CSP_CBF_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_CSP_SA_HEALTH_CB, evt.errors)
            self._read_activity_message = CONST.ERR_CSP_SA_HEALTH_CB + str(evt.errors)
            self.dev_logging(CONST.ERR_CSP_SA_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))

    def create_csp_ln_proxy(self):
        retry = 0
        proxy_created_flag = False
        print("self.CspSubarrayLNFQDN: ", self.CspSubarrayLNFQDN)
        while (retry < 3):
            try:
                self._csp_subarray_ln_proxy = DeviceProxy(self.CspSubarrayLNFQDN)
                print("CspSubarray proxy is: ", self._csp_subarray_ln_proxy)
                print("Cspp FQDN is: ", self.CspSubarrayLNFQDN)
                proxy_created_flag = True
                break
            except Exception as ex:
                print("exception: ", ex)
                retry += 1
                continue

        return proxy_created_flag

    def create_sdp_ln_proxy(self):
        retry = 0
        proxy_created_flag = False
        while (retry < 3):
            try:
                self._sdp_subarray_ln_proxy = DeviceProxy(self.SdpSubarrayLNFQDN)
                print("SdpSubarray proxy is: ", self._sdp_subarray_ln_proxy)
                print("Sdp FQDN is: ", self.SdpSubarrayLNFQDN)
                proxy_created_flag = True
                break
            except tango.DevFailed:
                retry += 1
                continue

        return proxy_created_flag

    def add_receptors_in_group(self, argin):
        """
        Creates tango group of the resources allocated in the subarray.

        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVarStringArray. List of receptor IDs to be allocated to subarray.
        :return:
            DevVarStringArray. List of Resources added to the Subarray.
        """
        excpt_count = 0
        excpt_msg = []
        allocation_success = []
        allocation_failure = []

        # Add each dish into the tango group
        for leafId in range(0, len(argin)):
            try:
                str_leafId = argin[leafId]
                self._dish_leaf_node_group.add(self.DishLeafNodePrefix +  str_leafId)
                devProxy = tango.DeviceProxy(self.DishLeafNodePrefix + str_leafId)
                self._dish_leaf_node_proxy.append(devProxy)
                # Update the list allocation_success with the dishes allocated successfully to subarray
                allocation_success.append(str_leafId)
                self._event_id = devProxy.subscribe_event(CONST.EVT_DISH_HEALTH_STATE,
                                                          tango.EventType.CHANGE_EVENT,
                                                          self.setHealth,
                                                          stateless=True)
                self.testDeviceVsEventID[devProxy] = self._event_id
                self._health_event_id.append(self._event_id)
                self._receptor_id_list.append(int(str_leafId))
                self.dishHealthStateMap[devProxy] = -1

                print(CONST.STR_TEST_DEV_VS_EVT_ID, self.testDeviceVsEventID)
                print(CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list(True))
                print(CONST.STR_LN_PROXIES, self._dish_leaf_node_proxy)
                self._read_activity_message = CONST.STR_GRP_DEF + str(
                    self._dish_leaf_node_group.get_device_list(True))
                self._read_activity_message = CONST.STR_LN_PROXIES + str(self._dish_leaf_node_proxy)
                print(CONST.STR_SUBS_HEALTH_ST_LN)
                self._read_activity_message = CONST.STR_SUBS_HEALTH_ST_LN
                print(CONST.STR_HS_EVNT_ID, self._health_event_id)
                self._read_activity_message = CONST.STR_HS_EVNT_ID + str(self._health_event_id)
                # Set state = ON
                self.set_state(DevState.ON)
                # set obsState to "IDLE"
                self._obs_state = 0
                self.set_status(CONST.STR_ASSIGN_RES_SUCCESS)
                self.dev_logging(CONST.STR_ASSIGN_RES_SUCCESS, int(tango.LogLevel.LOG_INFO))
            except DevFailed as dev_failed:
                print(CONST.ERR_ADDING_LEAFNODE, "\n", dev_failed)
                self._read_activity_message = CONST.ERR_ADDING_LEAFNODE + str(dev_failed)
                self.dev_logging(CONST.ERR_ADDING_LEAFNODE, int(tango.LogLevel.LOG_ERROR))
                excpt_msg.append(self._read_activity_message)
                excpt_count += 1
                allocation_failure.append(str_leafId)
                # Exception Logic to remove Id from subarray group
                group_dishes = self._dish_leaf_node_group.get_device_list()
                if group_dishes.contains(self.DishLeafNodePrefix +  str_leafId):
                    self._dish_leaf_node_group.remove(self.DishLeafNodePrefix + str_leafId)
                # unsubscribe event
                if self.testDeviceVsEventID[devProxy]:
                    devProxy.unsubscribe_event(self.testDeviceVsEventID[devProxy])
            except(DevFailed, Exception) as except_occurred:
                print(CONST.ERR_ASSIGN_RES_CMD, "\n", except_occurred)
                self._read_activity_message = CONST.ERR_ASSIGN_RES_CMD + str(except_occurred)
                self.dev_logging(CONST.ERR_ASSIGN_RES_CMD, int(tango.LogLevel.LOG_ERROR))
                excpt_msg.append(self._read_activity_message)
                excpt_count += 1

        # Throw Exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_ASSIGN_RES_EXEC, tango.ErrSeverity.ERR)
        return allocation_success


    def assign_csp_resources(self, argin):
        """
        This function assigns CSP resources to CSP Subarray through CSP Subarray Leaf
        Node.

        :param argin: List of strings
            Contains the list of strings that has the resources ids. Currently this list
             contains only receptor ids.

        :return: List of strings.
            Returns the list of successfully assigned resources. Currently the
            CSPSubarrayLeafNode.AssignResources function returns void. Thus, this
            function just loops back the input argument in case of success. In case of
            failure, empty list is returned.
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
            argout.append(argin)
        except DevFailed as df:
            print(CONST.ERR_CSP_CMD)
            self.dev_logging(CONST.ERR_CSP_CMD, int(tango.LogLevel.LOG_ERROR))
            self.dev_logging(df, int(tango.LogLevel.LOG_DEBUG))

        # For this PI CSP Subarray Leaf Node does not return anything. So this function is
        # looping the receptor ids back.
        return argout


    def assign_sdp_resources(self, argin):
        """
        This function assigns SDP resources to SDP Subarray through SDP Subarray Leaf
        Node.

        :param argin: List of strings
            Contains the list of strings that has the resources ids. Currently
            processing block ids are passed to this function.

        :return: List of strings.
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
            print(CONST.ERR_SDP_CMD)
            self.dev_logging(CONST.ERR_SDP_CMD, int(tango.LogLevel.LOG_ERROR))
            self.dev_logging(df, int(tango.LogLevel.LOG_DEBUG))

        # For this PI SDP Subarray Leaf Node does not return anything. So this function is
        # looping the processing block ids back.
        return argout

    def remove_receptors_in_group(self):
        """
                Deletes tango group of the resources allocated in the subarray.

                Note: Currently there are only receptors allocated so the group contains only receptor ids.

                :param argin:
                    DevVoid
                :return:
                    DevVoid
                """
        try:

            if self.testDeviceVsEventID != {}:
                print(CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True)))
                self._dish_leaf_node_group.remove_all()
                print(CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True)))
                self._read_activity_message = CONST.STR_GRP_DEF + str(
                    self._dish_leaf_node_group.get_device_list(True))
                print(CONST.STR_DISH_PROXY_LIST, self._dish_leaf_node_proxy)
                print(CONST.STR_HEALTH_ID, self._health_event_id)
                print(CONST.STR_TEST_DEV_VS_EVT_ID, self.testDeviceVsEventID)
                for dev in self.testDeviceVsEventID:
                    dev.unsubscribe_event(self.testDeviceVsEventID[dev])
                self.testDeviceVsEventID = {}
                self._health_event_id = []
                self._dish_leaf_node_proxy = []
                del self._receptor_id_list[:]
                self.set_status(CONST.STR_RECEPTORS_REMOVE_SUCCESS)
                self.dev_logging(CONST.STR_RECEPTORS_REMOVE_SUCCESS, int(tango.LogLevel.LOG_INFO))
        except DevFailed as dev_failed:
            print(CONST.ERR_RELEASE_RES_CMD_GROUP + str(dev_failed))
            self._read_activity_message = CONST.ERR_RELEASE_RES_CMD_GROUP + str(dev_failed)
            self._release_excpt_msg.append(self._read_activity_message)
            self._release_excpt_count += 1
        except Exception as except_occurred:
            print(CONST.ERR_RELEASE_RES_CMD, "\n", except_occurred)
            print(CONST.STR_DISH_PROXY_LIST, self._dish_leaf_node_proxy)
            print(CONST.STR_HEALTH_ID, self._health_event_id)
            self._read_activity_message = CONST.ERR_RELEASE_RES_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_RELEASE_RES_CMD, int(tango.LogLevel.LOG_ERROR))
            self._release_excpt_msg.append(self._read_activity_message)
            self._release_excpt_count += 1

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
            print(CONST.ERR_CSP_CMD)
            self.dev_logging(CONST.ERR_CSP_CMD, int(tango.LogLevel.LOG_ERROR))
            self.dev_logging(df, int(tango.LogLevel.LOG_DEBUG))

    def release_sdp_resources(self):
        """
            This function invokes releaseAllResources command on SDP Subarray via SDP Subarray Leaf Node.

            :param argin: DevVoid

            :return: DevVoid

        """
        try:
            self._sdp_subarray_ln_proxy.command_inout(CONST.CMD_RELEASE_ALL_RESOURCES)

        except DevFailed as df:
            print(CONST.ERR_SDP_CMD)
            self.dev_logging(CONST.ERR_SDP_CMD, int(tango.LogLevel.LOG_ERROR))
            self.dev_logging(df, int(tango.LogLevel.LOG_DEBUG))

    @command(
        dtype_in=('str',),
        doc_in="Execute Scan on the Subarray",
    )
    @DebugIt()
    def Scan(self, argin):
        """
        Schedules a scan for execution on a subarray. Command has a parameter which
        indicates the time (TAI) at which the Scan will start. Subarray transitions to
        obsState = SCANNING, when the execution of a scan starts.

        :param argin: String array with Scan start time as first element.

        :return: None
        """
        excpt_count = 0
        excpt_msg = []
        try:
            print(CONST.STR_SCAN_IP_ARG, argin)
            if type(float(argin[0])) == float:
                print("Observation state:", self._obs_state)
                assert self._obs_state != 3, CONST.SCAN_ALREADY_IN_PROGRESS
                print(CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list())
                self._read_activity_message = CONST.STR_SCAN_IP_ARG + str(argin)
                self._read_activity_message = CONST.STR_GRP_DEF + str(
                    self._dish_leaf_node_group.get_device_list())
                cmdData = tango.DeviceData()
                cmdData.insert(tango.DevString, argin[0])
                self._dish_leaf_node_group.command_inout(CONST.CMD_SCAN, cmdData)
                # set obsState to SCANNING when the scan is started
                self._obs_state = 3
                self.set_status(CONST.STR_SA_SCANNING)
                self.dev_logging(CONST.STR_SA_SCANNING, int(tango.LogLevel.LOG_INFO))
        except AssertionError as assert_error:
            print(CONST.ERR_SCAN_CMD, "\n", assert_error, CONST.ERR_DUPLICATE_SCAN_CMD)
            self._read_activity_message = CONST.ERR_DUPLICATE_SCAN_CMD + str(assert_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except ValueError as value_error:
            print(CONST.ERR_SCAN_CMD, value_error, CONST.ERR_INVALID_DATATYPE)
            self._read_activity_message = CONST.ERR_INVALID_DATATYPE + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except DevFailed as dev_failed:
            print(CONST.ERR_SCAN_CMD, str(dev_failed))
            self._read_activity_message = CONST.ERR_SCAN_CMD, str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occurred:
            print(CONST.ERR_SCAN_CMD, "\n", except_occurred)
            self._read_activity_message = CONST.ERR_SCAN_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        #Throw Exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_SCAN_EXEC, tango.ErrSeverity.ERR)

    def is_Scan_allowed(self):
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
    @command(
    )
    @DebugIt()
    def EndScan(self):
        """ Ends the scan. It can be either an automatic or an externally triggered transition
        after the scanning completes normally.

        :param argin: DevVoid.

        :return: None
        """
        excpt_count = 0
        excpt_msg = []
        try:
            assert self._obs_state == 3, CONST.SCAN_ALREADY_COMPLETED
            if self._obs_state == 3:
                print(CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list())
                cmdData = tango.DeviceData()
                cmdData.insert(tango.DevString, "0")
                self._dish_leaf_node_group.command_inout(CONST.CMD_END_SCAN, cmdData)
                # set obsState to IDLE when the scan is ended
                self._obs_state = 0
                self._scan_id = ""
                self._sb_id = ""
                self.set_status(CONST.STR_SCAN_COMPLETE)
                self.dev_logging(CONST.STR_SCAN_COMPLETE, int(tango.LogLevel.LOG_INFO))
        except DevFailed as dev_failed:
            print(CONST.ERR_END_SCAN_CMD_ON_GROUP, "\n", dev_failed)
            self._read_activity_message = CONST.ERR_END_SCAN_CMD_ON_GROUP + str(dev_failed)
            self.dev_logging(CONST.ERR_END_SCAN_CMD_ON_GROUP, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except AssertionError as assert_err:
            print(CONST.ERR_DUPLICATE_END_SCAN_CMD, "\n", assert_err)
            self._read_activity_message = CONST.ERR_DUPLICATE_END_SCAN_CMD
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occurred:
            print(CONST.ERR_END_SCAN_CMD, "\n", except_occurred)
            self._read_activity_message = CONST.ERR_END_SCAN_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_END_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # Throw Exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_END_SCAN_EXEC, tango.ErrSeverity.ERR)

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
        DevStrings . Upon successful execution, the 'receptorIDList' attribute of the
        given subarray is populated with the given receptors. And returns list of
        assigned resources as array of DevStrings.

        Note: Resource allocation for CSP and SDP resources is also implemented but
        currently CSP accepts only receptorIDList and SDP accepts only dummy resources.

        :param argin:
            DevVarStringArray. List of receptor IDs to be allocated to subarray.

        :return:
            DevVarStringArray. List of Resources added to the Subarray.
        """
        excpt_count = 0
        excpt_msg = []

        # 1. Argument validation
        try:
            # Allocation success and failure lists
            for leafId in range(0, len(argin)):
                float(argin[leafId])
        except ValueError as value_error:
            print(CONST.ERR_SCAN_CMD, "\n", value_error, CONST.ERR_INVALID_DATATYPE)
            self.dev_logging(CONST.ERR_INVALID_DATATYPE, int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_DATATYPE + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        with excpt_count is 0 and ThreadPoolExecutor(3) as executor:
            # 2.1 Create group of receptors
            self.dev_logging(CONST.STR_DISH_ALLOCATION, int(tango.LogLevel.LOG_INFO))
            dish_allocation_status = executor.submit(self.add_receptors_in_group, argin)

            # 2.2. Add resources in CSP subarray
            self.dev_logging(CONST.STR_CSP_ALLOCATION, int(tango.LogLevel.LOG_INFO))
            csp_allocation_status = executor.submit(self.assign_csp_resources, argin)

            # 2.3. Add resources in SDP subarray
            # For PI#3, TMC sends dummy resources to SDP.
            self.dev_logging(CONST.STR_SDP_ALLOCATION, int(tango.LogLevel.LOG_INFO))
            dummy_sdp_resources = ["PB1", "PB2"]
            sdp_allocation_status = executor.submit(self.assign_sdp_resources, dummy_sdp_resources)

            # 2.4 wait for result
            while (dish_allocation_status.done() == False or
                   csp_allocation_status.done() == False or
                   sdp_allocation_status.done() == False
            ):
                pass

            # 2.5. prepare return value
            dish_allocation_result = dish_allocation_status.result()
            log_msg = CONST.STR_DISH_ALLOCATION_RESULT + str(dish_allocation_result)
            self.dev_logging(log_msg, int(tango.LogLevel.LOG_DEBUG))
            print("dish_allocation_result: ", dish_allocation_result)

            csp_allocation_result = csp_allocation_status.result()
            log_msg = CONST.STR_CSP_ALLOCATION_RESULT + str(csp_allocation_result)
            self.dev_logging(log_msg, int(tango.LogLevel.LOG_DEBUG))
            print("csp_allocation_result: ", csp_allocation_result)

            sdp_allocation_result = sdp_allocation_status.result()
            log_msg = CONST.STR_SDP_ALLOCATION_RESULT + str(sdp_allocation_result)
            self.dev_logging(log_msg, int(tango.LogLevel.LOG_DEBUG))
            print("sdp_allocation_result: ", sdp_allocation_result)

            dish_allocation_result.sort()
            csp_allocation_result.sort()
            sdp_allocation_result.sort()
            argin.sort()
            dummy_sdp_resources.sort()
            if( dish_allocation_result == argin and
                csp_allocation_result == argin and
                sdp_allocation_result == dummy_sdp_resources
            ):
                # Currently sending only dish allocation results.
                # argout = dish_allocation_result
                argout = dish_allocation_result
            else:
                #TODO: Need to add code to revert allocated resources
                argout = []

        # return dish_allocation_result
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
        Releases all the resources from the subarray. If the command execution fails, array of receptors
        (device names) which are failed to be realeased from the subarray, is returned to Central Node.
        Upon successful execution, all the resources of a given subarray get released and empty array
        is returned.

        :param argin: DevVoid.

        :return: DevVarStringArray.
        """
        self._release_excpt_count = 0
        self._release_excpt_msg = []
        argout = []
        try:
            assert self.testDeviceVsEventID != {}, CONST.RESRC_ALREADY_RELEASED
            with self._release_excpt_count is 0 and ThreadPoolExecutor(3) as executor:
                # 1. Delete the group of receptors
                self.dev_logging(CONST.STR_DISH_RELEASE, int(tango.LogLevel.LOG_INFO))
                dish_release_status = executor.submit(self.remove_receptors_in_group)

                # Release resources from CSP Subarray
                self.dev_logging(CONST.STR_CSP_RELEASE, int(tango.LogLevel.LOG_INFO))
                csp_release_status = executor.submit(self.release_csp_resources)

                # Release resources from SDP Subarray
                self.dev_logging(CONST.STR_SDP_RELEASE, int(tango.LogLevel.LOG_INFO))
                sdp_release_status = executor.submit(self.release_sdp_resources)

                # 2.4 wait for result
                while (dish_release_status.done() == False or
                       csp_release_status.done() == False or
                       sdp_release_status.done() == False
                ):
                    pass

                self._scan_id = ""
                self._sb_id = ""
                self.set_state(DevState.OFF)  # Set state = OFF
                self._obs_state = 0  # set obsState to "IDLE"

        except AssertionError as assert_err:
            print(CONST.ERR_RELEASE_RES_CMD + str(assert_err))
            self._read_activity_message = CONST.ERR_RELEASE_RES_CMD + str(assert_err)
            self._release_excpt_msg.append(self._read_activity_message)
            self._release_excpt_count += 1

        # Throw Exception
        if self._release_excpt_count > 0:
            err_msg = ' '
            for item in self._release_excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_RELEASE_ALL_RES_EXEC, tango.ErrSeverity.ERR)


        argout.extend(self._dish_leaf_node_group.get_device_list(True))
        return argout

    def is_ReleaseAllResources_allowed(self):
        """Checks if ReleaseAllResources is allowed in the current state of SubarrayNode."""
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    def setHealth(self, evt):
        """
        Retrieves the subscribed DishMaster health state, aggregate them to evaluate
        health state of the Subarray.

        :param evt: A TANGO_CHANGE event on DishMaster healthState.

        :return: None

        """
        if evt.err is False:
            try:
                self._dish_health_state = evt.attr_value.value
                self.dishHealthStateMap[evt.device] = self._dish_health_state
                if self._dish_health_state == CONST.ENUM_OK:
                    print(CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_OK)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                                                                               ) + CONST.STR_OK
                elif self._dish_health_state == CONST.ENUM_DEGRADED:
                    print(CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_DEGRADED)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                                                                               ) + CONST.STR_DEGRADED
                elif self._dish_health_state == CONST.ENUM_FAILED:
                    print(CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_FAILED)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                                                                               ) + CONST.STR_FAILED
                elif self._dish_health_state == CONST.ENUM_UNKNOWN:
                    print(CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_UNKNOWN)
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                                                                               ) + CONST.STR_UNKNOWN
                else:
                    print(CONST.STR_HEALTH_STATE_UNKNOWN_VAL, evt)
                    self._read_activity_message = CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(evt)
                #Aggregated Health State
                failed_health_count = 0
                degraded_health_count = 0
                unknown_health_count = 0
                ok_health_count = 0
                for value in list(self.dishHealthStateMap.values()):
                    if value == 2:
                        failed_health_count = failed_health_count + 1
                        break
                    elif value == 1:
                        self._health_state = 1
                        degraded_health_count = degraded_health_count + 1
                    elif value == 3:
                        self._health_state = 3
                        unknown_health_count = unknown_health_count + 1
                    else:
                        self._health_state = 0
                        ok_health_count = ok_health_count + 1
                if ok_health_count == len(list(self.dishHealthStateMap.values())):
                    self._health_state = 0
                elif failed_health_count != 0:
                    self._health_state = 2
                elif degraded_health_count != 0:
                    self._health_state = 1
                else:
                    self._health_state = 3
            except KeyError as key_err:
                print(CONST.ERR_SETHEALTH_CALLBK, str(key_err))
                self._read_activity_message = CONST.ERR_SETHEALTH_CALLBK + str(key_err)
                self.dev_logging(CONST.ERR_SETHEALTH_CALLBK, int(tango.LogLevel.LOG_ERROR))
            except Exception as except_occurred:
                print(CONST.ERR_AGGR_HEALTH_STATE, except_occurred.message)
                self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(except_occurred.message)
                self.dev_logging(CONST.ERR_AGGR_HEALTH_STATE, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_SUBSR_SA_HEALTH_STATE, evt.errors)
            self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(evt.errors)
            self.dev_logging(CONST.ERR_SUBSR_SA_HEALTH_STATE, int(tango.LogLevel.LOG_ERROR))
    # PROTECTED REGION END #    //  SubarrayNode.class_variable

    # -----------------
    # Device Properties
    # -----------------

    DishLeafNodePrefix = device_property(
        dtype='str', default_value="ska_mid/tm_leaf_node/d",
        doc="Device name prefix for the Dish Leaf Node",
    )

    CspSubarrayLNFQDN = device_property(
        dtype='str', default_value="ska_mid/tm_leaf_node/csp_subarray01",
        doc="This property contains the FQDN of the CSP Subarray Leaf Node associated with the Subarray Node.",
    )

    SdpSubarrayLNFQDN = device_property(
        dtype='str', default_value="ska_mid/tm_leaf_node/sdp_subarray01",
        doc="This property contains the FQDN of the SDP Subarray Leaf Node associated with the Subarray Node.",
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
        self.SkaLevel = 2                       # set SKALevel to "2"
        self._admin_mode = 0                    # set adminMode to "ON-LINE"
        self._health_state = 0                  # set health state to "OK"
        self._obs_state = 0                     # set obsState to "IDLE"
        self._obs_mode = 0                     # set obsMode to "IDLE"
        self._simulation_mode = False
        self._scan_id = ""
        self._sb_id = ""
        self._receptor_id_list = []
        self.dishHealthStateMap = {}
        self._dish_leaf_node_group = tango.Group(CONST.GRP_DISH_LEAF_NODE)
        self._dish_leaf_node_proxy = []
        self._health_event_id = []
        self.testDeviceVsEventID = {}
        self.set_state(DevState.OFF)            # Set state = OFF
        self.csp_subarray_ln_health_state_map = {}
        self._subarray_health_state = CONST.ENUM_OK  #Aggregated

        # Create proxy for CSP Subarray Leaf Node
        self._csp_subarray_ln_proxy = None
        result = self.create_csp_ln_proxy()
        print("csp proxy creation result: ", result)

        # Create proxy for SDP Subarray Leaf Node
        self._sdp_subarray_ln_proxy = None
        self.create_sdp_ln_proxy()
        print("sdp proxy creation result: ", result)

        self._read_activity_message = CONST.STR_SA_INIT_SUCCESS
        self.set_status(CONST.STR_SA_INIT_SUCCESS)
        self.dev_logging(CONST.STR_SA_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))

        #Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
        try:
            #self.csp_subarray_ln_health_state_map[self._csp_subarray_ln_proxy] = -1
            self._csp_subarray_ln_proxy.subscribe_event(CONST.EVT_CSPSA_HEALTH, EventType.CHANGE_EVENT,
                                                        self.cspsubarrayHealthCallback, stateless=True)
            self.set_state(DevState.ON)
            self.set_status(CONST.STR_CSP_SA_LEAF_INIT_SUCCESS)
            self.dev_logging(CONST.STR_CSP_SA_LEAF_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except DevFailed as dev_failed:
            print(CONST.ERR_SUBS_CSP_SA_LEAF_ATTR, dev_failed)
            self._read_activity_message = CONST.ERR_SUBS_CSP_SA_LEAF_ATTR + str(dev_failed)
            self.set_state(DevState.FAULT)
            self.set_status(CONST.ERR_SUBS_CSP_SA_LEAF_ATTR)
            self.dev_logging(CONST.ERR_CSP_SA_LEAF_INIT, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  SubarrayNode.init_device

    # # Create device proxy for CSP Master Leaf Node
    # try:
    #     self._csp_master_leaf_proxy = DeviceProxy(self.CspMasterLeafNodeFQDN)
    #     self._csp_master_leaf_proxy.subscribe_event(CONST.EVT_SUBSR_CSP_MASTER_HEALTH,
    #                                                 EventType.CHANGE_EVENT,
    #                                                 self.healthStateCallback, stateless=True)
    # except DevFailed as dev_failed:
    #     print(CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH, self.CspMasterLeafNodeFQDN)
    #     self._read_activity_message = CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(
    #         self.CspMasterLeafNodeFQDN)
    #     self.dev_logging(CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH, int(tango.LogLevel.LOG_ERROR))
    #     print(CONST.STR_ERR_MSG, dev_failed)
    #     self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)






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
        """ Returns the Scan ID. """
        # PROTECTED REGION ID(SubarrayNode.scanID_read) ENABLED START #
        return self._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_sbID(self):
        """ Returns the scheduling block ID. """
        # PROTECTED REGION ID(SubarrayNode.sbID_read) ENABLED START #
        return self._sb_id
        # PROTECTED REGION END #    //  SubarrayNode.sbID_read

    def read_activityMessage(self):
        """ Returns activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    def read_receptorIDList(self):
        """ Returns the receptor IDs allocated to the Subarray. """
        # PROTECTED REGION ID(SubarrayNode.receptorIDList_read) ENABLED START #
        return self._receptor_id_list
        # PROTECTED REGION END #    //  SubarrayNode.receptorIDList_read

    # --------
    # Commands
    # --------

    @command(
        dtype_in=('str',),
        doc_in="Pointing parameters of Dish - Right ascension and Declination coordinates.",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SubarrayNode.Configure) ENABLED START #
        """
        Configures the resources assinged to the Subarray.

        :param argin: String array that includes pointing parameters of Dish - Azimuth and Elevation Angle.

        :return: None

        """
        excpt_count = 0
        excpt_msg = []
        try:
            self._read_activity_message = CONST.STR_CONFIGURE_IP_ARG + str(argin)
            self._read_activity_message = CONST.STR_GRP_DEF_CONFIGURE_FN + str(
                self._dish_leaf_node_group.get_device_list())
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevVarStringArray, argin)

            # set obsState to CONFIGURING when the configuration is started
            self._obs_state = 1
            self._dish_leaf_node_group.command_inout(CONST.CMD_CONFIGURE, cmdData)
            # set obsState to READY when the configuration is completed
            self._obs_state = 2
            self._scan_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self._sb_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self.dev_logging(CONST.STR_CONFIGURE_CMD_INVOKED_SA, int(tango.LogLevel.LOG_INFO))
        except DevFailed as dev_failed:
            print(CONST.ERR_CONFIGURE_CMD_GROUP, "\n", dev_failed)
            self._read_activity_message = CONST.ERR_CONFIGURE_CMD_GROUP + str(dev_failed)
            self.dev_logging(CONST.ERR_CONFIGURE_CMD_GROUP, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occurred:
            print(CONST.ERR_CONFIGURE_CMD, "\n", except_occurred)
            self._read_activity_message = CONST.ERR_CONFIGURE_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_CONFIGURE_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # Throw Exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  SubarrayNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(SubarrayNode.is_Configure_allowed) ENABLED START #
        """ Checks if the Configure command is allowed in the current state of the Subarray. """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
        # PROTECTED REGION END #    //  SubarrayNode.is_Configure_allowed

    @command(
        dtype_in='str',
        doc_in="Initial Pointing parameters of Dish - Right ascension and Declination coordinates.",
    )
    @DebugIt()
    def Track(self, argin):
        # PROTECTED REGION ID(SubarrayNode.Track) ENABLED START #
        """ Invokes Track command on the resources assigned to the Subarray.

        :param argin: DevString

        Argin to be provided is the Ra and Dec values in the following format: radec|2:31:50.91|89:15:51.4
        Where first value is tag that is radec, second value is Ra in Hr:Min:Sec, and third value is Dec in
        Deg:Min:Sec.

        :return: None

        """
        excpt_msg = []
        excpt_count = 0
        try:
            self._read_activity_message = CONST.STR_TRACK_IP_ARG + argin
            # set obsState to CONFIGURING when the configuration is started
            self._obs_state = 1
            cmd_input = []
            cmd_input.append(argin)
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevVarStringArray, cmd_input)
            self._dish_leaf_node_group.command_inout(CONST.CMD_TRACK, cmdData)
            # set obsState to READY when the configuration is completed
            self._obs_state = 2
            self._scan_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self._sb_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self.dev_logging(CONST.STR_TRACK_CMD_INVOKED_SA, int(tango.LogLevel.LOG_INFO))

        except tango.DevFailed as devfailed:
            excpt_msg.append(CONST.ERR_TRACK_CMD + ": " + \
                           str(devfailed.args[0].desc))
            excpt_count += 1
        except Exception as except_occured:
            print(CONST.ERR_TRACK_CMD, "\n", except_occured)
            self._read_activity_message = CONST.ERR_TRACK_CMD + str(except_occured)
            self.dev_logging(CONST.ERR_TRACK_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(CONST.ERR_TRACK_CMD + ": " + \
                             str(except_occured.args[0].desc))
            excpt_count += 1

        # throw exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_TRACK_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  SubarrayNode.Track

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
