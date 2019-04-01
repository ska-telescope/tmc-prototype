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
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SubarrayNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)

# tango imports
from builtins import str
from builtins import range
import tango
from tango import DebugIt, DevState, AttrWriteType, PipeWriteType, AttrQuality, DispLevel
from tango.server import run, Device, DeviceMeta, attribute, command, device_property
from skabase.SKASubarray.SKASubarray import SKASubarray

# Additional import
# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
import random
import string
import CONST
from future.utils import with_metaclass
# PROTECTED REGION END #    //  SubarrayNode.additionnal_import

__all__ = ["SubarrayNode", "main"]


class SubarrayNode(with_metaclass(DeviceMeta, SKASubarray)):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #

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
        try:
            print(CONST.STR_SCAN_IP_ARG, argin)
            if type(float(argin[0])) == float:
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
        except Exception as except_occured:
            print(CONST.ERR_SCAN_CMD, "\n", except_occured)
            self._read_activity_message = CONST.ERR_SCAN_CMD + str(except_occured)
            self.dev_logging(CONST.ERR_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))

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
        """
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
        except Exception as except_occured:
            print(CONST.ERR_END_SCAN_CMD, "\n", except_occured)
            self._read_activity_message = CONST.ERR_END_SCAN_CMD + str(except_occured)
            self.dev_logging(CONST.ERR_END_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))

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
         assigned resources as list of DevStrings.

        :param argin:
            DevVarStringArray. List of receptor IDs to be allocated to subarray.

        :return: List of Resources added to the Subarray.
            DevVarStringArray. List of receptors.
        """
        try:
            # Allocation success and failure lists
            allocation_success = []
            allocation_failure = []
            for leafId in range(0, len(argin)):
                if type(float(argin[leafId])) == float:
                    pass
            for leafId in range(0, len(argin)):
                try:
                    self._dish_leaf_node_group.add(self.DishLeafNodePrefix +  argin[leafId])
                    devProxy = tango.DeviceProxy(self.DishLeafNodePrefix + argin[leafId])
                    self._dish_leaf_node_proxy.append(devProxy)
                    # Update the list allocation_success with the dishes allocated successfully to subarray
                    allocation_success.append(argin[leafId])
                    self._event_id = devProxy.subscribe_event(CONST.EVT_DISH_HEALTH_STATE,
                                                              tango.EventType.CHANGE_EVENT,
                                                              self.setHealth,
                                                              stateless=True)
                    self.testDeviceVsEventID[devProxy] = self._event_id
                    self._health_event_id.append(self._event_id)
                    self._receptor_id_list.append(int(argin[leafId]))
                    self.dishHealthStateMap[devProxy] = -1

                except Exception as except_occured:
                    allocation_failure.append(argin[leafId])
                    # Exception Logic to remove Id from subarray group
                    group_dishes = self._dish_leaf_node_group.get_device_list()
                    if group_dishes.contains(self.DishLeafNodePrefix +  argin[leafId]):
                        self._dish_leaf_node_group.remove(self.DishLeafNodePrefix + argin[leafId])
                    # unsubscribe event
                    if self.testDeviceVsEventID[devProxy]:
                        devProxy.unsubscribe_event(self.testDeviceVsEventID[devProxy])

            print(CONST.STR_TEST_DEV_VS_EVT_ID, self.testDeviceVsEventID)
            print(CONST.STR_GRP_DEF, self._dish_leaf_node_group.get_device_list(True))
            print(CONST.STR_LN_PROXIES, self._dish_leaf_node_proxy)
            self._read_activity_message = CONST.STR_GRP_DEF + str(
                self._dish_leaf_node_group.get_device_list(True))
            self._read_activity_message = CONST.STR_LN_PROXIES + str(self._dish_leaf_node_proxy)
            print(CONST.STR_SUBS_HEALTH_ST_LN)
            self._read_activity_message = CONST.STR_SUBS_HEALTH_ST_LN
            print(CONST.STR_HS_EVNT_ID, self._health_event_id)
            self._read_activity_message = CONST.STR_HS_EVNT_ID +  str(self._health_event_id)
            # Set state = ON
            self.set_state(DevState.ON)
            # set obsState to "IDLE"
            self._obs_state = 0
            self.dev_logging(CONST.STR_ASSIGN_RES_SUCCESS, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_ASSIGN_RES_CMD, "\n", except_occured)
            self._read_activity_message = CONST.ERR_ASSIGN_RES_CMD + str(except_occured)
            self.dev_logging(CONST.ERR_ASSIGN_RES_CMD, int(tango.LogLevel.LOG_ERROR))
            argin = str(except_occured)
        return allocation_success

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
        Releases all the resources from the Subarray.
        :return: List of resources removed.
        """
        argout = []
        try:
            assert self.testDeviceVsEventID != {}, CONST.RESRC_ALREADY_RELEASED
            if self.testDeviceVsEventID != {}:
                print(CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True)))
                self._dish_leaf_node_group.remove_all()
                print(CONST.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True)))
                self._read_activity_message = CONST.STR_GRP_DEF + str(
                    self._dish_leaf_node_group.get_device_list(True))
                argout.extend(self._dish_leaf_node_group.get_device_list(True))
                print(CONST.STR_DISH_PROXY_LIST, self._dish_leaf_node_proxy)
                print(CONST.STR_HEALTH_ID, self._health_event_id)
                print(CONST.STR_TEST_DEV_VS_EVT_ID, self.testDeviceVsEventID)
                for dev in self.testDeviceVsEventID:
                    dev.unsubscribe_event(self.testDeviceVsEventID[dev])
                self.testDeviceVsEventID = {}
                self._health_event_id = []
                self._dish_leaf_node_proxy = []
                del self._receptor_id_list[:]
                self._scan_id = ""
                self._sb_id = ""
                self.set_state(DevState.OFF)    # Set state = OFF
                self._obs_state = 0             # set obsState to "IDLE"
                self.set_status(CONST.STR_RECEPTORS_REMOVE_SUCCESS)
                self.dev_logging(CONST.STR_RECEPTORS_REMOVE_SUCCESS, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_RELEASE_RES_CMD, "\n", except_occured)
            print(CONST.STR_DISH_PROXY_LIST, self._dish_leaf_node_proxy)
            print(CONST.STR_HEALTH_ID, self._health_event_id)
            self._read_activity_message = CONST.ERR_RELEASE_RES_CMD + str(except_occured)
            argout = []
            self.dev_logging(CONST.ERR_RELEASE_RES_CMD, int(tango.LogLevel.LOG_ERROR))
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
                elif degraded_health_count   != 0:
                    self._health_state = 1
                else:
                    self._health_state = 3
            except Exception as except_occured:
                print(CONST.ERR_AGGR_HEALTH_STATE, except_occured.message)
                self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(except_occured.message)
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
        doc = "Device name prefix for the Dish Leaf Node",
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
        self._read_activity_message = CONST.STR_SA_INIT_SUCCESS
        self.set_status(CONST.STR_SA_INIT_SUCCESS)
        self.dev_logging(CONST.STR_SA_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))
        # PROTECTED REGION END #    //  SubarrayNode.init_device

    def always_executed_hook(self):
        """ Internal construct of TANGO. """
        # PROTECTED REGION ID(SubarrayNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SubarrayNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SubarrayNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        pass
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
        doc_in="Pointing parameters of Dish - Azimuth and Elevation Angle.",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SubarrayNode.Configure) ENABLED START #
        """
        Configures the resources assinged to the Subarray.
        :param argin: String array that includes pointing parameters of Dish - Azimuth and Elevation Angle.
        :return: None
        """
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
        except Exception as except_occured:
            print(CONST.ERR_CONFIGURE_CMD, "\n", except_occured)
            self._read_activity_message = CONST.ERR_CONFIGURE_CMD + str(except_occured)
            self.dev_logging(CONST.ERR_CONFIGURE_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  SubarrayNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(SubarrayNode.is_Configure_allowed) ENABLED START #
        """ Checks if the Configure command is allowed in the current state of the Subarray. """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]
        # PROTECTED REGION END #    //  SubarrayNode.is_Configure_allowed

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
