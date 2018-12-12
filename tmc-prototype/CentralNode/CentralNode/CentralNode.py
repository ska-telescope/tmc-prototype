# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" CentralNode

Central Node is a coordinator of the complete M&C system.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
from tango import DeviceProxy, DevState, EventType, utils, DeviceData
# PROTECTED REGION END #    //  CentralNode.additionnal_import

__all__ = ["CentralNode", "main"]


class CentralNode(SKABaseDevice):
    """
    Central Node is a coordinator of the complete M&C system.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #

    def subarrayHealthStateCallback(self, evt):

        if (evt.err==False):
            try:
                self._subarray_health_state = evt.attr_value.value
                if "tm_subarray_node/1" in evt.attr_name:
                    self._subarray1_health_state = self._subarray_health_state
                elif "tm_subarray_node/2" in evt.attr_name:
                    self._subarray2_health_state = self._subarray_health_state
                else:
                    print "Event from the Unknown Subarray device!"
                    self._read_activity_message = "Event from the Unknown Subarray device!"

                self.subarrayHealthStateMap[evt.device] = self._subarray_health_state
                if (self._subarray_health_state == 0):
                    print "Health state of " + str(evt.device) + " :-> OK"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> OK"
                elif (self._subarray_health_state == 1):
                    print "Health state of " + str(evt.device) + " :-> DEGRADED"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> DEGRADED"
                elif (self._subarray_health_state == 2):
                    print "Health state of " + str(evt.device) + " :-> FAILED"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> FAILED"
                elif (self._subarray_health_state == 3):
                    print "Health state of " + str(evt.device) + " :-> UNKNOWN"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> UNKNOWN"
                else:
                    print "Subarray Health state event returned unknown value! \n", evt
                    self._read_activity_message = "Subarray Health state event returned unknown value! \n" + str(evt)
                # Aggregated Health State
                failed = 0
                degraded = 0
                unknown = 0
                ok = 0
                for value in (self.subarrayHealthStateMap.values()):
                    if value == 2:
                        failed = failed + 1
                        break
                    elif value == 1:
                        self._telescope_health_state = 1
                        degraded = degraded + 1
                    elif value == 3:
                        self._telescope_health_state = 3
                        unknown = unknown + 1

                    else:
                        self._telescope_health_state = 0
                        ok = ok + 1

                if ok == len(self.subarrayHealthStateMap.values()):
                    self._telescope_health_state = 0

                elif failed != 0:
                    self._telescope_health_state = 2

                elif degraded != 0:
                    self._telescope_health_state = 1

                else:
                    self._telescope_health_state = 3

            except Exception as e:
                print "Unexpected error while aggregating Health state!\n", e
                self._read_activity_message = "Unexpected error while aggregating Health state!\n" + str(e)
                self.devlogmsg("Unexpected error while aggregating Health state!", 2)
        else:
            print "Error event on subscribing Subarray HealthState!\n", evt
            self._read_activity_message = "Error event on subscribing Subarray HealthState!\n" + str(evt)
            self.devlogmsg("Error event on subscribing Subarray HealthState!", 2)
    '''
    class subarrayStateCallback (utils.EventCallback):
        def push_event(self, evt):

            if (evt.err==False):
                try:
                    self._dish_mode = evt.attr_value.value
                    if(self._dish_mode == 0):
                        print "Dish Mode :-> OFF"
                    elif (self._dish_mode == 1):
                        print "Dish Mode :-> STARTUP"
                    elif (self._dish_mode == 2):
                        print "Dish Mode :->  SHUTDOWN"
                    elif (self._dish_mode == 3):
                        print "Dish Mode :->  STANDBY-LP"
                    elif (self._dish_mode == 4):
                        print "Dish Mode :-> STANDBY-FP"
                    elif (self._dish_mode == 5):
                        print "Dish Mode :-> MAINTENANCE"
                    elif (self._dish_mode == 6):
                        print "Dish Mode :-> STOW"
                    elif (self._dish_mode == 7):
                        print "Dish Mode :-> CONFIG"
                    elif (self._dish_mode == 8):
                        print "Dish Mode :-> OPERATE"
                    else:
                        print "Dish Mode :-> UNKNOWN!\n", evt
                except Exception as e:
                    print "Unexpected error in DishModeCallback!\n", e.message
            else:
                print "Error event on subscribing DishMode attribute!\n", evt.errors

    class subarrayObsStateCallback (utils.EventCallback):
        def push_event(self, evt):

            if (evt.err==False):
                try:
                    self._dish_mode = evt.attr_value.value
                    if(self._dish_mode == 0):
                        print "Dish Mode :-> OFF"
                    elif (self._dish_mode == 1):
                        print "Dish Mode :-> STARTUP"
                    elif (self._dish_mode == 2):
                        print "Dish Mode :->  SHUTDOWN"
                    elif (self._dish_mode == 3):
                        print "Dish Mode :->  STANDBY-LP"
                    elif (self._dish_mode == 4):
                        print "Dish Mode :-> STANDBY-FP"
                    elif (self._dish_mode == 5):
                        print "Dish Mode :-> MAINTENANCE"
                    elif (self._dish_mode == 6):
                        print "Dish Mode :-> STOW"
                    elif (self._dish_mode == 7):
                        print "Dish Mode :-> CONFIG"
                    elif (self._dish_mode == 8):
                        print "Dish Mode :-> OPERATE"
                    else:
                        print "Dish Mode :-> UNKNOWN!\n", evt
                except Exception as e:
                    print "Unexpected error in DishModeCallback!\n", e.message
            else:
                print "Error event on subscribing DishMode attribute!\n", evt.errors


    class subarrayReceptorIDListCallback (utils.EventCallback):
        def push_event(self, evt):

            if (evt.err==False):
                try:
                    print "Event attribute value is: " , evt.attr_value.value

                except Exception as e:
                    print "Unexpected error in receptorIDListCallback!\n", e.message
            else:
                print "Error event on subscribing receptorIDList attribute!\n", evt.errors
    '''
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
        dtype=('str',), default_value=["ska_mid/tm_subarray_node/1", "ska_mid/tm_subarray_node/2"]
    )

    NumDishes = device_property(
        dtype='uint', default_value=4
    )

    DishLeafNodePrefix = device_property(
        dtype='str', default_value="ska_mid/tm_leaf_node/d"
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
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CentralNode.init_device) ENABLED START #
        try:
            # To read forwarded attributes
            #print "Subarray 1 Health:", self.subarray1HealthState
            #print "Subarray 2 Health:",self.subarray2HealthState.get_x()

            self._subarray1_health_state = 0
            self._subarray2_health_state = 0

            self.set_state(PyTango.DevState.ON)
            # Initialise Properties
            self.SkaLevel = 1

            # Initialise Attributes
            self._health_state = 0
            self._admin_mode = 0
            self._telescope_health_state = 0
            self.subarrayHealthStateMap = {}
            self._dish_leaf_node_devices = []
            self._leaf_device_proxy = []

        except Exception as e:
            print "Unexpected error on initialising properties and attributes on Central Node device."
            self._read_activity_message = "Unexpected error on initialising properties and attributes on Central Node device."
            self.devlogmsg("Unexpected error in initialising properties and attributes on Central Node device.", 2)
            self._read_activity_message = "Error message is: \n" + str(e)
            print "Error message is: \n", e

        #  Get Dish Leaf Node devices List
        self.db = PyTango.Database()
        try:
            self.dev_DbDatum = self.db.get_device_exported("ska_mid/tm_leaf_node/d000*")
            self._dish_leaf_node_devices.extend(self.dev_DbDatum.value_string)
            print self._dish_leaf_node_devices

        except Exception as e:
            print "Unexpected error in reading exported Dish Leaf Node device names from database \n", e
            self._read_activity_message = "Unexpected error in reading exported Dish Leaf Node device names from database \n" + str(e)
            self.devlogmsg(
                "Unexpected error in reading exported Dish Leaf Node device names from database \n", 2)

        # Create proxies of Dish Leaf Node devices

        for name in range (0,len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy.append(DeviceProxy(self._dish_leaf_node_devices[name]))

            except Exception as e:
                print "Unexpected error in creating proxy of the device ", self._dish_leaf_node_devices[name]
                self._read_activity_message = "Unexpected error in creating proxy of the device " +  str(self._dish_leaf_node_devices[name])
                print "Error message is: \n", e
                self._read_activity_message = "Error message is: \n" + str(e)
                self.devlogmsg(
                    "Unexpected error in creating proxy of the device ", 2)
        print self._leaf_device_proxy

        '''
        # Subscribing Subarray Nodes Attributes
        
        #subarrayStateCallback = self.subarrayStateCallback()
        #subarrayObsStateCallback = self.subarrayObsStateCallback()
        #subarrayReceptorIDListCallback = self.subarrayReceptorIDListCallback()
        '''
        for subarray in range(0, len(self.TMMidSubarrayNodes)):
            try:
                subarray_proxy = DeviceProxy(self.TMMidSubarrayNodes[subarray])
                self.subarrayHealthStateMap[subarray_proxy] = -1
                subarray_proxy.subscribe_event("healthState", EventType.CHANGE_EVENT, self.subarrayHealthStateCallback, stateless=True)
                #subarray_proxy.subscribe_event("state", EventType.CHANGE_EVENT, subarrayStateCallback, stateless=True)
                #subarray_proxy.subscribe_event("obsState", EventType.CHANGE_EVENT, subarrayObsStateCallback, stateless=True)
                #subarray_proxy.subscribe_event("receptorIDList", EventType.CHANGE_EVENT, subarrayReceptorIDListCallback, stateless=True)

            except Exception as e:
                print "Exception occurred while subscribing to attributes of", self.TMMidSubarrayNodes[subarray]
                self._read_activity_message = "Exception occurred while subscribing to attributes of" + str(self.TMMidSubarrayNodes[subarray])
                self.devlogmsg(
                    "Exception occurred while subscribing to attributes of Subarray", 2)
                print "error message is: " , e
                self._read_activity_message = "Error message is: " + str(e)


        # PROTECTED REGION END #    //  CentralNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CentralNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CentralNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CentralNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CentralNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_telescopeHealthState(self):
        # PROTECTED REGION ID(CentralNode.telescopeHealthState_read) ENABLED START #
        '''
        if ((self._subarray1_health_state == 0) & (self._subarray2_health_state == 0)):
            self._telescope_health = 0
        elif ((self._subarray1_health_state == 2) & (self._subarray2_health_state == 2)):
            self._telescope_health = 2
        elif ((self._subarray1_health_state == 1) | (self._subarray2_health_state == 1)):
            self._telescope_health = 1
        else:
            self._telescope_health = 3

        '''
        return self._telescope_health_state
        # PROTECTED REGION END #    //  CentralNode.telescopeHealthState_read

    def read_subarray1HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray1HealthState_read) ENABLED START #
        return self._subarray1_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray1HealthState_read

    def read_subarray2HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray2HealthState_read) ENABLED START #
        return self._subarray2_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray2HealthState_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CentralNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  CentralNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CentralNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CentralNode.activityMessage_write


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
        self.devlogmsg("STOW command invoked from Central node on the requested dishes", 4)
        self._read_activity_message = "STOW command invoked from Central node on the requested dishes"

        for i in range(0,len(argin)):
            device_name = self.DishLeafNodePrefix + argin[i]

            try:
                device_proxy = PyTango.DeviceProxy(device_name)
                device_proxy.command_inout("SetStowMode")
            except Exception as e:
                print "Unexpected error in executing STOW command on ", device_name
                self._read_activity_message = "Unexpected error in executing STOW command on " + str(device_name)
                print "Error message is: \n", e
                self._read_activity_message = "Error message is: \n" + str(e)
                self.devlogmsg("Unexpected error in executing STOW command!", 2)

        # PROTECTED REGION END #    //  CentralNode.StowAntennas

    @command(
    )
    @DebugIt()
    def StandByTelescope(self):
        # PROTECTED REGION ID(CentralNode.StandByTelescope) ENABLED START #
        self.devlogmsg("StandByTelescope command invoked from Central node", 4)
        self._read_activity_message = "StandByTelescope command invoked from Central node"

        for name in range (0,len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy[name].command_inout("SetStandbyLPMode")
            except Exception as e:
                print "Unexpected error in setting Standby mode on ", self._dish_leaf_node_devices[name]
                self._read_activity_message = "Unexpected error in setting Standby mode on " + str(self._dish_leaf_node_devices[name])
                print "Error message is: \n", e
                self._read_activity_message = "Error message is: \n" + str(e)
                self.devlogmsg("Unexpected error in executing StandByTelescope command!", 2)

        # PROTECTED REGION END #    //  CentralNode.StandByTelescope

    @command(
    )
    @DebugIt()
    def StartUpTelescope(self):
        # PROTECTED REGION ID(CentralNode.StartUpTelescope) ENABLED START #
        self.devlogmsg("StartUpTelescope command invoked from Central node", 4)
        self._read_activity_message = "StartUpTelescope command invoked from Central node"

        for name in range (0,len(self._dish_leaf_node_devices)):
            try:
                print self._leaf_device_proxy
                self._leaf_device_proxy[name].command_inout("SetOperateMode")
            except Exception as e:
                print "Unexpected error in StartUp of ", self._dish_leaf_node_devices[name]
                self._read_activity_message = "Unexpected error in StartUp of " + str(self._dish_leaf_node_devices[name])
                print "Error message is: \n", e
                self._read_activity_message = "Error message is: \n" + str(e)
                self.devlogmsg("Unexpected error in executing StartUpTelescope command!", 2)
        # PROTECTED REGION END #    //  CentralNode.StartUpTelescope

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CentralNode.main) ENABLED START #
    return run((CentralNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CentralNode.main

if __name__ == '__main__':
    main()
