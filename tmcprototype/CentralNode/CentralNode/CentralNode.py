# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
Central Node is a coordinator of the complete M&C system. Central Node implements the standard set
of state and mode attributes defined by the SKA Control Model.
"""
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CentralNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)

# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, DeviceMeta, attribute, command, device_property
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice

# Additional import

# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import CONST
from future.utils import with_metaclass
import json
# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = ["CentralNode", "main"]


class CentralNode(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    Central Node is a coordinator of the complete M&C system.
    """
    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #

    def healthStateCallback(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.
        :param evt: A TANGO_CHANGE event on Subarray healthState.
        :return: None
        """
        if evt.err is False:
            try:
                health_state = evt.attr_value.value
                if CONST.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    self._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif CONST.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    self._subarray2_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif CONST.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    self._subarray3_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif self.CspMasterLeafNodeFQDN in evt.attr_name:
                    self._csp_master_leaf_health = health_state
                elif self.SdpMasterLeafNodeFQDN in evt.attr_name:
                    self._sdp_master_leaf_health = health_state
                else:
                    print(CONST.EVT_UNKNOWN)
                    # self._read_activity_message = CONST.EVT_UNKNOWN

                if health_state == CONST.ENUM_OK:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_OK)
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                    #                                                            ) + CONST.STR_OK
                elif health_state == CONST.ENUM_DEGRADED:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_DEGRADED)
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                    #                                                            ) + CONST.STR_DEGRADED
                elif health_state == CONST.ENUM_FAILED:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_FAILED)
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                    #                                                            ) + CONST.STR_FAILED
                elif health_state == CONST.ENUM_UNKNOWN:
                    print(CONST.STR_HEALTH_STATE + str(evt.device
                                                       ) + CONST.STR_UNKNOWN)
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(
                    #     evt.device) + CONST.STR_UNKNOWN
                else:
                    print(CONST.STR_HEALTH_STATE_UNKNOWN_VAL, evt)
                    # self._read_activity_message = CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(evt)
                # Aggregated Health State
                failed_health_count = 0
                degraded_health_count = 0
                unknown_health_count = 0
                ok_health_count = 0

                # Check the health state of CSP and SDP Master Leaf Nodes
                if (self._csp_master_leaf_health == CONST.ENUM_OK or
                        self._sdp_master_leaf_health == CONST.ENUM_OK ):
                    ok_health_count = 1
                elif (self._csp_master_leaf_health == CONST.ENUM_DEGRADED or
                        self._sdp_master_leaf_health == CONST.ENUM_DEGRADED):
                    degraded_health_count = 1
                elif (self._csp_master_leaf_health == CONST.ENUM_FAILED or
                        self._sdp_master_leaf_health == CONST.ENUM_FAILED ):
                    failed_health_count = 1
                else:
                    unknown_health_count = 1

                for value in list(self.subarray_health_state_map.values()):
                    if value == CONST.ENUM_FAILED:
                        failed_health_count = failed_health_count + 1
                        break
                    elif value == CONST.ENUM_DEGRADED:
                        degraded_health_count = degraded_health_count + 1
                    elif value == CONST.ENUM_UNKNOWN:
                        unknown_health_count = unknown_health_count + 1
                    else:
                        ok_health_count = ok_health_count + 1
                if ok_health_count == len(list(self.subarray_health_state_map.values())) + 2:
                    self._telescope_health_state = CONST.ENUM_OK
                elif failed_health_count != 0:
                    self._telescope_health_state = CONST.ENUM_FAILED
                elif degraded_health_count != 0:
                    self._telescope_health_state = CONST.ENUM_DEGRADED
                else:
                    self._telescope_health_state = CONST.ENUM_UNKNOWN
            except KeyError as key_error:
                print(CONST.ERR_SUBARRAY_HEALTHSTATE, key_error)
                # self._read_activity_message = CONST.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
                self.dev_logging(CONST.ERR_SUBARRAY_HEALTHSTATE, int(tango.LogLevel.LOG_FATAL))
            except DevFailed as dev_failed:
                print(CONST.ERR_SUBSR_SA_HEALTH_STATE, dev_failed)
                # self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                self.dev_logging(CONST.ERR_SUBSR_SA_HEALTH_STATE, int(tango.LogLevel.LOG_FATAL))
            except Exception as except_occured:
                print(CONST.ERR_AGGR_HEALTH_STATE, except_occured)
                # self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(except_occured)
                self.dev_logging(CONST.ERR_AGGR_HEALTH_STATE, int(tango.LogLevel.LOG_FATAL))
        else:
            print(CONST.ERR_SUBSR_SA_HEALTH_STATE, evt)
            # self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
            self.dev_logging(CONST.ERR_SUBSR_SA_HEALTH_STATE, int(tango.LogLevel.LOG_FATAL))
    # PROTECTED REGION END #    //  CentralNode.class_variable

    # -----------------
    # Device Properties
    # -----------------
    CentralAlarmHandler = device_property(
        dtype='str',
        doc="Device name of CentralAlarmHandler ",
    )

    TMAlarmHandler = device_property(
        dtype='str',
        doc="Device name of TMAlarmHandler ",
    )

    TMMidSubarrayNodes = device_property(
        dtype=('str',), doc="List of TM Mid Subarray Node devices",
    )

    NumDishes = device_property(
        dtype='uint', default_value=1,
        doc="Number of Dishes",
    )

    DishLeafNodePrefix = device_property(
        dtype='str', doc="Device name prefix for Dish Leaf Node"
    )

    CspMasterLeafNodeFQDN = device_property(
        dtype='str'
    )

    SdpMasterLeafNodeFQDN = device_property(
        dtype='str'
    )

    # ----------
    # Attributes
    # ----------

    telescopeHealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="Health state of Telescope",
    )

    subarray1HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="Health state of Subarray1",
    )

    subarray2HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="Health state of Subarray2",
    )
    subarray3HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        # PROTECTED REGION ID(CentralNode.init_device) ENABLED START #
        """ Initializes the attributes and properties of the Central Node. """
        try:
            SKABaseDevice.init_device(self)
            self._subarray1_health_state = CONST.ENUM_OK
            self._subarray2_health_state = CONST.ENUM_OK
            self._subarray3_health_state = CONST.ENUM_OK
            self.set_state(DevState.ON)
            # Initialise Properties
            self.SkaLevel = CONST.INT_SKA_LEVEL
            # Initialise Attributes
            self._health_state = CONST.ENUM_OK
            self._admin_mode = CONST.ENUM_ONLINE
            self._telescope_health_state = CONST.ENUM_OK
            self.subarray_health_state_map = {}
            self._dish_leaf_node_devices = []
            self._leaf_device_proxy = []
            self.subarray_FQDN_dict = {}
            self._subarray_allocation = {}
            self.set_status(CONST.STR_INIT_SUCCESS)
        except DevFailed as dev_failed:
            print(CONST.ERR_INIT_PROP_ATTR_CN)
            self._read_activity_message = CONST.ERR_INIT_PROP_ATTR_CN
            self.dev_logging(CONST.ERR_INIT_PROP_ATTR_CN, int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            print(CONST.STR_ERR_MSG, dev_failed)
        #  Get Dish Leaf Node devices List
        # TODO: Getting DishLeafNode devices list from TANGO DB
        # self.tango_db = PyTango.Database()
        # try:
        #     self.dev_dbdatum = self.tango_db.get_device_exported(CONST.GET_DEVICE_LIST_TANGO_DB)
        #     self._dish_leaf_node_devices.extend(self.dev_bdatum.value_string)
        #     print self._dish_leaf_node_devices
        #
        # except Exception as except_occured:
        #     print CONST.ERR_IN_READ_DISH_LN_DEVS, except_occured
        #     self._read_activity_message = CONST.ERR_IN_READ_DISH_LN_DEVS + str(except_occured)
        #     self.dev_logging(CONST.ERR_IN_READ_DISH_LN_DEVS, int(tango.LogLevel.LOG_ERROR))

        for dish in range(1, (self.NumDishes+1)):

            # Update self._dish_leaf_node_devices variable
            print("DishLeafNodePrefix:", self.DishLeafNodePrefix)
            self._dish_leaf_node_devices.append(self.DishLeafNodePrefix + "000" + str(dish))

            # Initialize self.subarray_allocation variable to indicate availability of the dishes
            dish_ID = "dish000" + str(dish)
            self._subarray_allocation[dish_ID] = "NOT_ALLOCATED"

        # Create proxies of Dish Leaf Node devices
        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy.append(DeviceProxy(self._dish_leaf_node_devices[name]))
            except (DevFailed, KeyError) as except_occurred:
                print(CONST.ERR_IN_CREATE_PROXY, self._dish_leaf_node_devices[name])
                self._read_activity_message = CONST.ERR_IN_CREATE_PROXY + \
                                              str(self._dish_leaf_node_devices[name])
                print(CONST.STR_ERR_MSG, except_occurred)
                self._read_activity_message = CONST.STR_ERR_MSG + str(except_occurred)
                self.dev_logging(CONST.ERR_IN_CREATE_PROXY, int(tango.LogLevel.LOG_ERROR))

        # Create device proxy for CSP Master Leaf Node
        try:
            self._csp_master_leaf_proxy = DeviceProxy(self.CspMasterLeafNodeFQDN)
            self._csp_master_leaf_proxy.subscribe_event(CONST.EVT_SUBSR_CSP_MASTER_HEALTH,
                                                        EventType.CHANGE_EVENT,
                                                        self.healthStateCallback, stateless=True)
        except DevFailed as dev_failed:
            print(CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH, self.CspMasterLeafNodeFQDN)
            self._read_activity_message = CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(
                self.CspMasterLeafNodeFQDN)
            self.dev_logging(CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, dev_failed)
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)

        # Create device proxy for SDP Master Leaf Node
        try:
            self._sdp_master_leaf_proxy = DeviceProxy(self.SdpMasterLeafNodeFQDN)
            self._sdp_master_leaf_proxy.subscribe_event(CONST.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                        EventType.CHANGE_EVENT,
                                                        self.healthStateCallback, stateless=True)
        except DevFailed as dev_failed:
            print(CONST.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH, self.SdpMasterLeafNodeFQDN)
            self._read_activity_message = CONST.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH + str(
                self.SdpMasterLeafNodeFQDN)
            self.dev_logging(CONST.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, dev_failed)
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)

        for subarray in range(0, len(self.TMMidSubarrayNodes)):
            try:
                subarray_proxy = DeviceProxy(self.TMMidSubarrayNodes[subarray])
                self.subarray_health_state_map[subarray_proxy] = -1
                subarray_proxy.subscribe_event(CONST.EVT_SUBSR_HEALTH_STATE,
                                               EventType.CHANGE_EVENT,
                                               self.healthStateCallback, stateless=True)

                #populate subarrayID-subarray proxy map
                tokens = self.TMMidSubarrayNodes[subarray].split('/')
                subarrayID = int(tokens[2])
                self.subarray_FQDN_dict[subarrayID] = subarray_proxy
            except DevFailed as dev_failed:
                print(CONST.ERR_SUBSR_SA_HEALTH_STATE, self.TMMidSubarrayNodes[subarray])
                self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + \
                                              str(self.TMMidSubarrayNodes[subarray])
                self.dev_logging(CONST.ERR_SUBSR_SA_HEALTH_STATE, int(tango.LogLevel.LOG_ERROR))
                print(CONST.STR_ERR_MSG, dev_failed)
                self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)

        # PROTECTED REGION END #    //  CentralNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CentralNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CentralNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CentralNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CentralNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_telescopeHealthState(self):
        # PROTECTED REGION ID(CentralNode.telescope_healthstate_read) ENABLED START #
        """ Returns the Telescope health state."""
        return self._telescope_health_state
        # PROTECTED REGION END #    //  CentralNode.telescope_healthstate_read

    def read_subarray1HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray1_healthstate_read) ENABLED START #
        """ Returns Subarray1 health state. """
        return self._subarray1_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray1_healthstate_read

    def read_subarray2HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray2_healthstate_read) ENABLED START #
        """ Returns Subarray2 health state. """
        return self._subarray2_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray2_healthstate_read

    def read_subarray3HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray3HealthState_read) ENABLED START #
        """ Returns Subarray3 health state. """
        return self._subarray3_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray3HealthState_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CentralNode.activity_message_read) ENABLED START #
        """ Returns activity message. """
        return self._read_activity_message
        # PROTECTED REGION END #    //  CentralNode.activity_message_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CentralNode.activity_message_write) ENABLED START #
        """ Sets the activity message. """
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CentralNode.activity_message_write

    # --------
    # Commands
    # --------

    @command(
        dtype_in=('str',),
        doc_in="List of Receptors to be stowed",
    )
    @DebugIt()
    def StowAntennas(self, argin):
        # PROTECTED REGION ID(CentralNode.StowAntennas) ENABLED START #
        """
        Stows the specified receptors.
        :param argin: List of Receptors to be stowed.
        :return: None
        """
        excpt_count = 0
        excpt_msg = []
        try:
            for leafId in range(0, len(argin)):
                if type(float(argin[leafId])) == float:
                    pass
            self.dev_logging(CONST.STR_STOW_CMD_ISSUED_CN, int(tango.LogLevel.LOG_INFO))
            self._read_activity_message = CONST.STR_STOW_CMD_ISSUED_CN
            for i in range(0, len(argin)):
                device_name = self.DishLeafNodePrefix + argin[i]
                try:
                    device_proxy = DeviceProxy(device_name)
                    device_proxy.command_inout(CONST.CMD_SET_STOW_MODE)
                except DevFailed as dev_failed:
                    print(CONST.ERR_EXE_STOW_CMD, device_name)
                    self._read_activity_message = CONST.ERR_EXE_STOW_CMD + str(device_name)
                    excpt_msg.append(self._read_activity_message)
                    print(CONST.STR_ERR_MSG, dev_failed)
                    self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
                    self.dev_logging(CONST.STR_ERR_MSG, int(tango.LogLevel.LOG_ERROR))
                    excpt_msg.append(self._read_activity_message)
                    excpt_count += 1

                # throw exception:
                if excpt_count > 0:
                    err_msg = ' '
                    for item in excpt_msg:
                        err_msg += item + "\n"
                    tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                                 CONST.STR_STOW_ANTENNA_EXEC, tango.ErrSeverity.ERR)
        except ValueError as value_error:
            print(CONST.ERR_STOW_ARGIN, value_error)
            self._read_activity_message = CONST.ERR_STOW_ARGIN + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occured:
            print(CONST.ERR_EXE_STOW_CMD, except_occured)
            self._read_activity_message = CONST.ERR_EXE_STOW_CMD + str(except_occured)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_STOW_ANTENNA_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  CentralNode.stow_antennas

    @command(
    )
    @DebugIt()
    def StandByTelescope(self):
        # PROTECTED REGION ID(CentralNode.StandByTelescope) ENABLED START #
        """ Set the Elements into STANDBY state (i.e. Low Power State). """
        excpt_count =0
        excpt_msg =[]
        self.dev_logging(CONST.STR_STANDBY_CMD_ISSUED, int(tango.LogLevel.LOG_INFO))
        self._read_activity_message = CONST.STR_STANDBY_CMD_ISSUED
        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy[name].command_inout(CONST.CMD_SET_STANDBY_MODE)
            except DevFailed as dev_failed:
                print(CONST.ERR_EXE_STANDBY_CMD, self._dish_leaf_node_devices[name])
                self._read_activity_message = CONST.ERR_EXE_STANDBY_CMD + \
                                              str(self._dish_leaf_node_devices[name])
                excpt_msg.append(self._read_activity_message)
                print(CONST.STR_ERR_MSG, dev_failed)
                self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
                self.dev_logging(CONST.ERR_EXE_STANDBY_CMD, int(tango.LogLevel.LOG_ERROR))
                excpt_msg.append(self._read_activity_message)
                excpt_count += 1
        try:
            self._csp_master_leaf_proxy.command_inout(CONST.CMD_STANDBY, [])
        except DevFailed as dev_failed:
            print(CONST.ERR_EXE_STANDBY_CMD, self.CspMasterLeafNodeFQDN)
            self._read_activity_message = CONST.ERR_EXE_STANDBY_CMD + str(self.CspMasterLeafNodeFQDN)
            print(CONST.STR_ERR_MSG, dev_failed)
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            self.dev_logging(CONST.ERR_EXE_STANDBY_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        try:
            self._sdp_master_leaf_proxy.command_inout(CONST.CMD_STANDBY)
        except DevFailed as dev_failed:
            print(CONST.ERR_EXE_STANDBY_CMD, self.SdpMasterLeafNodeFQDN)
            self._read_activity_message = CONST.ERR_EXE_STANDBY_CMD + str(self.SdpMasterLeafNodeFQDN)
            print(CONST.STR_ERR_MSG, dev_failed)
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            self.dev_logging(CONST.ERR_EXE_STANDBY_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

            # throw exception:
            if excpt_count > 0:
                err_msg = ' '
                for item in excpt_msg:
                    err_msg += item + "\n"
                tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                             CONST.STR_STANDBY_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  CentralNode.standby_telescope

    @command(
    )
    @DebugIt()
    def StartUpTelescope(self):
        # PROTECTED REGION ID(CentralNode.StartUpTelescope) ENABLED START #
        """ Set the Elements into ON state from STANDBY state."""
        excpt_count =0
        excpt_msg = []
        self.dev_logging(CONST.STR_STARTUP_CMD_ISSUED, int(tango.LogLevel.LOG_INFO))
        self._read_activity_message = CONST.STR_STARTUP_CMD_ISSUED
        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy[name].command_inout(CONST.CMD_SET_OPERATE_MODE)
            except DevFailed as dev_failed:
                print(CONST.ERR_EXE_STARTUP_CMD, self._dish_leaf_node_devices[name])
                self._read_activity_message = CONST.ERR_EXE_STARTUP_CMD + \
                                              str(self._dish_leaf_node_devices[name])
                excpt_msg.append(self._read_activity_message)
                print(CONST.STR_ERR_MSG, dev_failed)
                self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
                self.dev_logging(CONST.ERR_EXE_STARTUP_CMD, int(tango.LogLevel.LOG_ERROR))
                excpt_msg.append(self._read_activity_message)
                excpt_count += 1

        try:
            self._csp_master_leaf_proxy.command_inout(CONST.CMD_STARTUP,
                                                      [])
        except Exception as except_occured:
            print(CONST.ERR_EXE_STARTUP_CMD, self.CspMasterLeafNodeFQDN)
            self._read_activity_message = CONST.ERR_EXE_STARTUP_CMD + str(self.CspMasterLeafNodeFQDN)
            print(CONST.STR_ERR_MSG, except_occured)
            self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)
            self.dev_logging(CONST.ERR_EXE_STARTUP_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        try:
            self._sdp_master_leaf_proxy.command_inout(CONST.CMD_STARTUP)
        except DevFailed as dev_failed:
            print(CONST.ERR_EXE_STARTUP_CMD, self.SdpMasterLeafNodeFQDN)
            self._read_activity_message = CONST.ERR_EXE_STARTUP_CMD + str(self.SdpMasterLeafNodeFQDN)
            print(CONST.STR_ERR_MSG, dev_failed)
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            self.dev_logging(CONST.ERR_EXE_STARTUP_CMD, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

            # throw exception:
            if excpt_count > 0:
                err_msg = ' '
                for item in excpt_msg:
                    err_msg += item + "\n"
                tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                             CONST.STR_STARTUP_EXEC, tango.ErrSeverity.ERR)


        # PROTECTED REGION END #    //  CentralNode.startup_telescope

    @command(
        dtype_in='str',
        doc_in="The string in JSON format. The JSON contains following values:\nsubarrayID: "
        "DevShort\ndish: JSON object consisting\n- receptorIDList: DevVarStringArray. "
        "The individual string should contain dish numbers in string format with "
        "preceding zeroes upto 3 digits. E.g. 0001, 0002",
        dtype_out='str',
        doc_out="The string in JSON format. The JSON contains following values:\ndish:"
        " JSON object consisting receptors allocated successfully: DevVarStringArray."
        " The individual string should contain dish numbers in string format with "
        "preceding zeroes upto 3 digits. E.g. 0001, 0002", )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(CentralNode.AssignResources) ENABLED START #
        """
        Assigns resources to given subarray. It accepts the subarray id and
        receptor id list in JSON string format. Upon successful execution, the
        'receptorIDList' attribute of the given subarray is populated with the given
        receptors.

        :param argin: The string in JSON format. The JSON contains following values:


            subarrayID:
                DevShort. Mandatory.

            dish:
                Mandatory JSON object consisting of

                receptorIDList:
                    DevVarStringArray
                    The individual string should contain dish numbers in string format
                    with preceding zeroes upto 3 digits. E.g. 0001, 0002.

            Example:
                {
                "subarrayID": 1,
                "dish": {
                "receptorIDList": ["0001", "0002"]
                }
                }

        Note: From Jive, enter input as:
        {"subarrayID":1,"dish":{"receptorIDList":["0001"]}} without any space.

        :return: The string in JSON format. The JSON contains following values:

            dish:
                Mandatory JSON object consisting of

                receptorIDList_success:
                    DevVarStringArray
                    Contains ids of the receptors which are successfully allocated. Empty on unsuccessful
                    allocation.


            Example:
                {
                "dish": {
                "receptorIDList_success": ["0001", "0002"]
                }
                }
        """
        receptorIDList = []
        excpt_msg = []
        excpt_count = 0
        argout = []
        try:
            # serialize the json
            jsonArgument = json.loads(argin)
            # Create subarray proxy
            subarrayID = int(jsonArgument['subarrayID'])
            subarrayProxy = self.subarray_FQDN_dict[subarrayID]
            # Check for the duplicate receptor allocation
            duplicate_allocation_count = 0
            duplicate_allocation_dish_ids = []
            input_receptor_list = jsonArgument["dish"]["receptorIDList"]
            len_input_receptor_list= len(input_receptor_list)
            for dish in range(0, len_input_receptor_list):
                dish_ID = "dish" + input_receptor_list[dish]
                if self._subarray_allocation[dish_ID] != "NOT_ALLOCATED":
                    duplicate_allocation_dish_ids.append(dish_ID)
                    duplicate_allocation_count = duplicate_allocation_count + 1
            if duplicate_allocation_count == 0:
                self._resources_allocated = subarrayProxy.command_inout(
                    CONST.CMD_ASSIGN_RESOURCES, jsonArgument["dish"]["receptorIDList"])
                # Update self._subarray_allocation variable to update subarray allocation
                # for the related dishes.
                # Also append the allocated dish to out argument.
                for dish in range(0, len(self._resources_allocated)):
                    dish_ID = "dish" + (self._resources_allocated[dish])
                    self._subarray_allocation[dish_ID] = "SA" + str(subarrayID)
                    receptorIDList.append(self._resources_allocated[dish])

                self._read_activity_message = CONST.STR_ASSIGN_RESOURCES_SUCCESS
                self.dev_logging(CONST.STR_ASSIGN_RESOURCES_SUCCESS, int(tango.LogLevel.LOG_INFO))
                argout = {
                    "dish": {
                        "receptorIDList_success": receptorIDList
                    }
                }
            else:
                print(CONST.STR_DISH_DUPLICATE, duplicate_allocation_dish_ids)
                self._read_activity_message = CONST.STR_DISH_DUPLICATE+ str(duplicate_allocation_dish_ids)
                argout = {
                    "dish": {
                        "receptorIDList_success": receptorIDList
                    }
                }
        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
            print("ValueError")
        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
            print("KeyError")
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_ASSGN_RESOURCES + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ASSGN_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_ASSGN_RESOURCES + str(except_occurred), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ASSGN_RESOURCES + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        #throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_ASSIGN_RES_EXEC, tango.ErrSeverity.ERR)
            argout = '{"dish": {"receptorIDList_success": []}}'

        # For future reference
        #argout['dish']['receptorIDList'] = receptorIDList
        #argout['receptorIDList'] = receptorIDList
        return json.dumps(argout)
        # PROTECTED REGION END #    //  CentralNode.AssignResources

    @command(dtype_in='str', dtype_out='str', )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(CentralNode.ReleaseResources) ENABLED START #

        """
        Release all the resources of given Subarray. It accepts the subarray id, releaseALL flag and
        receptorIDList in JSON string format. When the releaseALL flag is True, ReleaseAllResources command
        is         invoked on the respective subarray. In this case, the receptorIDList tag is empty as all
        the resources of the Subarray are released.
        When releaseALL is False, ReleaseResources will be invoked on the Subarray and the resources provided
        in receptorIDList tag, are released from Subarray. This selective release of the resources when
        releaseALL is False, will be implemented in the later stages of the prototype.

        :param argin: The string in JSON format. The JSON contains following values:

            subarrayID:
                DevShort. Mandatory.

            releaseALL:
                Boolean(True or False). Mandatory. True when all the resources to be released from Subarray.

            receptorIDList:
                DevVarStringArray. Empty when releaseALL tag is True.

            Example:
                {
                    "subarrayID": 1,
                    "releaseALL": true,
                    "receptorIDList": []
                }


            Note: From Jive, enter input as:
                {"subarrayID":1,"releaseALL":true,"receptorIDList":[]} without any space.

            :return: argout: The string in JSON format. The JSON contains following values:

                releaseALL:
                    Boolean(True or False). If True, all the resources are successfully released from the
                    Subarray.

                receptorIDList:
                    DevVarStringArray. If releaseALL is True, receptorIDList is empty. Else list returns
                    resources (device names) that are noe released from the subarray.

                Example:
                    argout =
                    {
                        "ReleaseAll" : True,
                        "receptorIDList" : []
                    }
        """
        excpt_count = 0
        excpt_msg =[]
        try:
            release_success = False
            res_not_released = []
            jsonArgument = json.loads(argin)
            subarrayID = jsonArgument['subarrayID']
            subarrayProxy = self.subarray_FQDN_dict[subarrayID]
            subarray_name = "SA" + str(subarrayID)
            if jsonArgument['releaseALL'] == True:
                res_not_released = subarrayProxy.command_inout(CONST.CMD_RELEASE_RESOURCES)
                self._read_activity_message = CONST.STR_REL_RESOURCES
                self.dev_logging(CONST.STR_REL_RESOURCES, int(tango.LogLevel.LOG_INFO))
                if not res_not_released:
                    release_success = True
                    for Dish_ID, Dish_Status in self._subarray_allocation.items():
                        if Dish_Status == subarray_name:
                            self._subarray_allocation[Dish_ID] = "NOT_ALLOCATED"
                else:
                    self._read_activity_message = CONST.STR_LIST_RES_NOT_REL \
                                                  + res_not_released
                    release_success = False
            else:
                self._read_activity_message = CONST.STR_FALSE_TAG
        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_RELEASE_RESOURCES + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_RELEASE_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_RELEASE_RES_EXEC, tango.ErrSeverity.ERR)

        argout = {
            "ReleaseAll" : release_success,
            "receptorIDList" : res_not_released
        }
        return json.dumps(argout)
        # PROTECTED REGION END #    //  CentralNode.ReleaseResource
# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(CentralNode.main) ENABLED START #
    """
    Runs the CentralNode.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: CentralNode TANGO object.
    """
    return run((CentralNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CentralNode.main

if __name__ == '__main__':
    main()
