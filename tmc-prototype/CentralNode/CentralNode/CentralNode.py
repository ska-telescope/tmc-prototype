# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""
Central Node is a coordinator of the complete M&C system. Central Node implements the standard set
of state and mode attributes defined by the SKA Control Model.
"""

# tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType
from tango.server import run, DeviceMeta, attribute, command, device_property
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import CONST
# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = ["CentralNode", "main"]


class CentralNode(SKABaseDevice):
    """
    Central Node is a coordinator of the complete M&C system.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #
    def subarrayHealthStateCallback(self, evt):
        """
        :param evt: A TANGO_CHANGE event of Subarray's healthState attribute
        :return:
        This method retrieves individual subarray health state, aggregates them to calculate the
        telescope health state.
        """
        if evt.err is False:
            try:
                self._subarray_health_state = evt.attr_value.value
                if CONST.EVT_SA1_NODE in evt.attr_name:
                    self._subarray1_health_state = self._subarray_health_state
                elif CONST.EVT_SA2_NODE in evt.attr_name:
                    self._subarray2_health_state = self._subarray_health_state
                else:
                    print CONST.EVT_UNKNOWN_SA
                    self._read_activity_message = CONST.EVT_UNKNOWN_SA

                self.subarrayHealthStateMap = self._subarray_health_state
                if self._subarray_health_state == CONST.ENUM_OK:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_OK
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)\
                                                  + CONST.STR_OK
                elif self._subarray_health_state == CONST.STR_DEGRADED:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_DEGRADED
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)\
                                                  + CONST.STR_DEGRADED
                elif self._subarray_health_state == CONST.STR_FAILED:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_FAILED
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)\
                     + CONST.STR_FAILED
                elif self._subarray_health_state == CONST.ENUM_UNKNOWN:
                    print CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_UNKNOWN
                    self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device)\
                     + CONST.STR_UNKNOWN
                else:
                    print CONST.STR_HEALTH_STATE_UNKNOWN_VAL, evt
                    self._read_activity_message = CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(evt)
                # Aggregated Health State
                failed = 0
                degraded = 0
                unknown = 0
                _ok = 0
                for value in self.subarrayHealthStateMap.values():
                    if value == CONST.ENUM_FAILED:
                        failed = failed + 1
                        break
                    elif value == CONST.ENUM_DEGRADED:
                        self._telescope_health_state = 1
                        degraded = degraded + 1
                    elif value == CONST.ENUM_UNKNOWN:
                        self._telescope_health_state = CONST.ENUM_UNKNOWN
                        unknown = unknown + 1

                    else:
                        self._telescope_health_state = CONST.ENUM_OK
                        _ok = _ok + 1

                if _ok == len(self.subarrayHealthStateMap.values()):
                    self._telescope_health_state = CONST.ENUM_OK

                elif failed != 0:
                    self._telescope_health_state = CONST.ENUM_FAILED

                elif degraded != 0:
                    self._telescope_health_state = CONST.ENUM_DEGRADED

                else:
                    self._telescope_health_state = CONST.ENUM_UNKNOWN

            except Exception as except_occured:
                print CONST.ERR_AGGR_HEALTH_STATE, except_occured
                self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(except_occured)
                self.devlogmsg(CONST.ERR_AGGR_HEALTH_STATE, 1)
        else:
            print CONST.ERR_SUBSR_SA_HEALTH_STATE, evt
            self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
            self.devlogmsg(CONST.ERR_SUBSR_SA_HEALTH_STATE, 1)

    # PROTECTED REGION END #    //  CentralNode.class_variable

    # -----------------
    # Device Properties
    # -----------------

    CentralAlarmHandler = device_property(
        dtype='str',
    )

    TMAlarmHandler = device_property(
        dtype='str',
    )

    TMMidSubarrayNodes = device_property(
        dtype=('str',), default_value=[CONST.PROP_DEF_VAL_TM_MID_SA1, CONST.PROP_DEF_VAL_TM_MID_SA2]
    )

    NumDishes = device_property(
        dtype='uint', default_value=4
    )

    DishLeafNodePrefix = device_property(
        dtype='str', default_value=CONST.PROP_DEF_VAL_LEAF_NODE_PREFIX
    )


    # ----------
    # Attributes
    # ----------











    telescopeHealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    subarray1HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    subarray2HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------
    def init_device(self):
        # PROTECTED REGION ID(CentralNode.init_device) ENABLED START #
        """ This method initializes the attributes and properties"""
        SKABaseDevice.init_device(self)
        try:
            # To read forwarded attributes
            # print "Subarray 1 Health:", self.subarray1HealthState
            # print "Subarray 2 Health:",self.subarray2HealthState.get_x()

            self._subarray1_health_state = CONST.ENUM_OK
            self._subarray2_health_state = CONST.ENUM_OK

            self.set_state(tango.DevState.ON)
            # Initialise Properties
            self.SkaLevel = CONST.INT_SKA_LEVEL

            # Initialise Attributes
            self._health_state = CONST.ENUM_OK
            self._admin_mode = 0
            self._telescope_health_state = CONST.ENUM_OK
            self.subarrayHealthStateMap = {}
            self._dish_leaf_node_devices = []
            self._leaf_device_proxy = []


        except Exception as except_occured:
            print CONST.ERR_INIT_PROP_ATTR_CN
            self._read_activity_message = CONST.ERR_INIT_PROP_ATTR_CN
            self.devlogmsg(CONST.ERR_INIT_PROP_ATTR_CN, 2)
            self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)
            print CONST.STR_ERR_MSG, except_occured

        #  Get Dish Leaf Node devices List
        self.tango_db = tango.Database()
        try:
            self.dev_dbdatum = self.tango_db.get_device_exported(CONST.GET_DEVICE_LIST_TANGO_DB)
            self._dish_leaf_node_devices.extend(self.dev_dbdatum.value_string)
            print self._dish_leaf_node_devices

        except Exception as except_occured:
            print CONST.ERR_IN_READ_DISH_LN_DEVS, except_occured
            self._read_activity_message = CONST.ERR_IN_READ_DISH_LN_DEVS + str(except_occured)
            self.devlogmsg(CONST.ERR_IN_READ_DISH_LN_DEVS, 2)

        # Create proxies of Dish Leaf Node devices

        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy.append(DeviceProxy(self._dish_leaf_node_devices[name]))

            except Exception as except_occured:
                print CONST.ERR_IN_CREATE_PROXY, self._dish_leaf_node_devices[name]
                self._read_activity_message = CONST.ERR_IN_CREATE_PROXY \
                                              + str(self._dish_leaf_node_devices[name])
                print CONST.STR_ERR_MSG, except_occured
                self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)
                self.devlogmsg(CONST.ERR_IN_CREATE_PROXY, 2)
        print self._leaf_device_proxy

        for subarray in range(0, len(self.TMMidSubarrayNodes)):
            try:
                subarray_proxy = DeviceProxy(self.TMMidSubarrayNodes[subarray])
                self.subarrayHealthStateMap[subarray_proxy] = -1
                subarray_proxy.subscribe_event(CONST.EVT_SUBSR_SA_HEALTH_STATE,
                                               EventType.CHANGE_EVENT,
                                               self.subarrayHealthStateCallback, stateless=True)
                # subarray_proxy.subscribe_event("state", EventType.CHANGE_EVENT,
                # subarrayStateCallback, stateless=True)
                # subarray_proxy.subscribe_event("obsState", EventType.CHANGE_EVENT,
                # subarrayObsStateCallback, stateless=True)
                # subarray_proxy.subscribe_event("receptorIDList", EventType.CHANGE_EVENT,
                # subarrayReceptorIDListCallback, stateless=True)

            except Exception as except_occured:
                print CONST.ERR_SUBSR_SA_HEALTH_STATE, self.TMMidSubarrayNodes[subarray]
                self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE\
                                              + str(self.TMMidSubarrayNodes[subarray])
                self.devlogmsg(CONST.ERR_SUBSR_SA_HEALTH_STATE, 2)
                print CONST.STR_ERR_MSG, except_occured
                self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)

        # PROTECTED REGION END #    //  CentralNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CentralNode.always_executed_hook) ENABLED START #
        """ This method is an internal construct of TANGO"""
        pass
        # PROTECTED REGION END #    //  CentralNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CentralNode.delete_device) ENABLED START #
        """ This method is an internal construct of TANGO"""
        pass
        # PROTECTED REGION END #    //  CentralNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_telescopeHealthState(self):
        # PROTECTED REGION ID(CentralNode.telescope_healthstate_read) ENABLED START #
        """ This method reads the Telescope health state."""
        return self._telescope_health_state
        # PROTECTED REGION END #    //  CentralNode.telescope_healthstate_read

    def read_subarray1HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray1_healthstate_read) ENABLED START #
        """ This method reads the subarray 1 health state"""
        return self._subarray1_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray1_healthstate_read

    def read_subarray2HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray2_healthstate_read) ENABLED START #
        """ This method reads the subarray 2 health state"""
        return self._subarray2_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray2_healthstate_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CentralNode.activity_message_read) ENABLED START #
        """ This method reads activity message """
        return self._read_activity_message
        # PROTECTED REGION END #    //  CentralNode.activity_message_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CentralNode.activity_message_write) ENABLED START #
        """ This method reads activity message intended to write on the GUI"""
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
        :param argin: List of Receptors to be stowed.
        :return:
        This method is to stow the specified receptors.
        This method is useful when an operator wants to stow a group of dishes.
        """
        self.devlogmsg(CONST.STR_STOW_CMD_ISSUED_CN, 4)
        self._read_activity_message = CONST.STR_STOW_CMD_ISSUED_CN

        for i in range(0, len(argin)):
            device_name = self.DishLeafNodePrefix + argin[i]

            try:
                device_proxy = tango.DeviceProxy(device_name)
                device_proxy.command_inout(CONST.CMD_SET_STOW_MODE)
            except Exception as except_occured:
                print CONST.ERR_EXE_STOW_CMD, device_name
                self._read_activity_message = CONST.ERR_EXE_STOW_CMD + str(device_name)
                print CONST.STR_ERR_MSG, except_occured
                self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)
                self.devlogmsg(CONST.STR_ERR_MSG, 2)
        # PROTECTED REGION END #    //  CentralNode.stow_antennas

    @command(
    )
    @DebugIt()
    def StandByTelescope(self):
        # PROTECTED REGION ID(CentralNode.StandByTelescope) ENABLED START #
        """ This command is to bring the Telescope into a STANDBY state (i.e. Low Power State) """
        self.devlogmsg(CONST.STR_STANDBY_CMD_ISSUED, 4)
        self._read_activity_message = CONST.STR_STANDBY_CMD_ISSUED

        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy[name].command_inout(CONST.CMD_SET_STANDBY_MODE)
            except Exception as except_occured:
                print CONST.ERR_EXE_STANDBY_CMD, self._dish_leaf_node_devices[name]
                self._read_activity_message = CONST.ERR_EXE_STANDBY_CMD \
                                              + str(self._dish_leaf_node_devices[name])
                print CONST.STR_ERR_MSG, except_occured
                self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)
                self.devlogmsg(CONST.ERR_EXE_STANDBY_CMD, 2)
        # PROTECTED REGION END #    //  CentralNode.standby_telescope

    @command(
    )
    @DebugIt()
    def StartUpTelescope(self):
        # PROTECTED REGION ID(CentralNode.StartUpTelescope) ENABLED START #
        """ This command is to bring the Telescope into ON state from the STANDBY state."""
        self.devlogmsg(CONST.STR_STARTUP_CMD_ISSUED, 4)
        self._read_activity_message = CONST.STR_STARTUP_CMD_ISSUED

        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                print self._leaf_device_proxy
                self._leaf_device_proxy[name].command_inout(CONST.CMD_SET_OPERATE_MODE)
            except Exception as except_occured:
                print CONST.ERR_EXE_STARTUP_CMD, self._dish_leaf_node_devices[name]
                self._read_activity_message = CONST.ERR_EXE_STARTUP_CMD \
                                              + str(self._dish_leaf_node_devices[name])
                print CONST.STR_ERR_MSG, except_occured
                self._read_activity_message = CONST.STR_ERR_MSG + str(except_occured)
                self.devlogmsg(CONST.ERR_EXE_STARTUP_CMD, 2)
        # PROTECTED REGION END #    //  CentralNode.startup_telescope

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CentralNode.main) ENABLED START #
    """
    :param args:
    :param kwargs:
    :return:
    This method runs the CentralNode class.
    """
    return run((CentralNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CentralNode.main

if __name__ == '__main__':
    main()
