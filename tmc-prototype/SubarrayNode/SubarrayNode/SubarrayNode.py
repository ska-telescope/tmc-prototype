# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Subarray Node

Provides the monitoring and control interface required by users as well as 
other TM Components (such as OET, Central Node) for a Subarray.
"""

# PyTango imports
import random
import string

import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKASubarray import SKASubarray
# Additional import
# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
import tango
# PROTECTED REGION END #    //  SubarrayNode.additionnal_import

__all__ = ["SubarrayNode", "main"]


class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as 
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #

    @command(
        dtype_in=('str',),
        doc_in="Execute Scan on the Subarray",
    )
    @DebugIt()
    def Scan(self, argin):

        try:
            
            print "Scan inputs Arguments :-> ", argin
            print "Group Definitions in scan function :-> ", self._dish_leaf_node_group.get_device_list()

            self._read_activity_message = "Scan inputs Arguments :-> " + str(argin)
            self._read_activity_message = "Group Definitions in scan function :-> " + str(self._dish_leaf_node_group.get_device_list())

            cmdData = PyTango.DeviceData()
            cmdData.insert(PyTango.DevString, argin[0])
            self._dish_leaf_node_group.command_inout("Scan", cmdData)
            self._obs_state = 3                                                                                         # set obsState to SCANNING when the scan is started
            self.set_status("Subarray is scanning at the desired pointing coordinates.")
            self.devlogmsg("Subarray is scanning at the desired pointing coordinates.", 4)

        except Exception as e:
            print "Exception in Scan command:"
            print e

            self._read_activity_message = "Exception in Scan command: \n " + str(e)

            self.devlogmsg("Exception occurred while Subarray is scanning at the desired pointing coordinates.", 2)

    def is_Scan_allowed(self):
        return self.get_state() not in [DevState.FAULT,DevState.UNKNOWN,DevState.DISABLE,DevState.STANDBY]
    
    @command(
    )
    @DebugIt()
    def EndScan(self):

        try:
            print "Group Definitions in EndScan function :-> ", self._dish_leaf_node_group.get_device_list()
            cmdData = PyTango.DeviceData()
            cmdData.insert(PyTango.DevString, "0")
            self._dish_leaf_node_group.command_inout("EndScan", cmdData)
            self._obs_state = 0                                                                                         # set obsState to IDLE when the scan is ended
            self.set_status("Scan is completed")
            self.devlogmsg("Scan is completed", 4)
        except Exception as e:
            print "Exception in EndScan command:"
            print e

            self._read_activity_message = "Exception in EndScan command: \n " + str(e)

            self.devlogmsg("Exception occurred while ending the scan on Subarray.", 2)

    def is_EndScan_allowed(self):
        return self.get_state() not in [DevState.FAULT,DevState.UNKNOWN,DevState.DISABLE,DevState.STANDBY]


    @command(
        dtype_in=('str',),
        doc_in="List of Resources to add to subarray.",
        dtype_out=('str',),
        doc_out="A list of Resources added to the subarray.",
    )
    @DebugIt()
    def AssignResources(self, argin):

        try:

            for leafId in range(0, len(argin)):
                self._dish_leaf_node_group.add(self.DishLeafNodePrefix +  argin[leafId])
                devProxy = PyTango.DeviceProxy(self.DishLeafNodePrefix + argin[leafId])
                self._dish_leaf_node_proxy.append(devProxy)
                self._event_id = devProxy.subscribe_event("dishHealthState",
                                                        PyTango.EventType.CHANGE_EVENT,
                                                        self.setHealth,
                                                        stateless=True)
                self.testDeviceVsEventID[devProxy] = self._event_id
                self._health_event_id.append(self._event_id)
                self._receptor_id_list.append(int(argin[leafId]))
                self.dishHealthStateMap[devProxy] = -1
            print 'self.testDeviceVsEventID ', self.testDeviceVsEventID
            print "Group definition :-> ", self._dish_leaf_node_group.get_device_list(True)
            print "LeafNode proxies :-> ", self._dish_leaf_node_proxy

            self._read_activity_message = "Group definition :-> " + str(self._dish_leaf_node_group.get_device_list(True))
            self._read_activity_message = "LeafNode proxies :-> " + str(self._dish_leaf_node_proxy)

            print "Subscribing HealthState attributes of Leaf Nodes..."

            self._read_activity_message = "Subscribing HealthState attributes of Leaf Nodes..."

            '''for leaf in range(0, len(self._dish_leaf_node_proxy)):
                self.dishHealthStateMap[self._dish_leaf_node_proxy[leaf]] = -1



            for leaf in range(0, len(self._dish_leaf_node_proxy)):
                self._event_id = (self._dish_leaf_node_proxy[leaf]).subscribe_event("dishHealthState",
                                                                                  PyTango.EventType.CHANGE_EVENT,
                                                                                  self.setHealth,
                                                                                  stateless=True)
                 

            # for leaf in range(len(self._dish_leaf_node_proxy)-1, len(self._dish_leaf_node_proxy)-1-len(argin), -1 ):
            #     self._event_id = self._dish_leaf_node_proxy[leaf].subscribe_event("dishHealthState",
            #                                                                            PyTango.EventType.CHANGE_EVENT,
            #                                                                            self.setHealth,
            #                                                                            stateless=True)
            #

            # self._health_event_id.append(self._dish_leaf_node_proxy[0].subscribe_event("dishHealthState",
            #                                                                             PyTango.EventType.CHANGE_EVENT,
            #                                                                             self.setHealth,
            #                                                                             stateless=True))
            # self._health_event_id.append(self._dish_leaf_node_proxy[1].subscribe_event("dishHealthState",
            #                                                                               PyTango.EventType.CHANGE_EVENT,
            #                                                                               self.setHealth,
            #                                                                               stateless=True))


                self._health_event_id.append(self._event_id)'''
            print "DishHealth EventID array is:" , self._health_event_id

            self._read_activity_message = "DishHealth EventID array is:" +  str(self._health_event_id)

            self.set_state(DevState.ON)                                                                                 # Set state = ON
            self._obs_state = 0                                                                                         # set obsState to "IDLE"
            self.set_status("Receptors are assigned successfully.")
            self.devlogmsg("Receptors are assigned successfully.", 4)

        except Exception as e:
            print "Exception in AssignResources command:"
            print e

            self._read_activity_message = "Exception in AssignResources command: \n " + str(e)

            self.devlogmsg("Exception occurred in AssignResources command.", 2)
            argin = str(e)

        return argin

    def is_AssignResources_allowed(self):
        return self.get_state() not in [DevState.FAULT,DevState.UNKNOWN,DevState.DISABLE,DevState.STANDBY]

    @command(
        dtype_out=('str',),
        doc_out="List of resources removed from the subarray.",
    )
    @DebugIt()
    def ReleaseAllResources(self):

        argout = []
        try:
            print "Group definition in release function:-> " + str(self._dish_leaf_node_group.get_device_list(True))
            self._dish_leaf_node_group.remove_all()
            print "Group definition in release function after removal:-> "+ str(self._dish_leaf_node_group.get_device_list(True))

            self._read_activity_message = "Group definition in release function:-> " + str(self._dish_leaf_node_group.get_device_list(True))

            argout.extend(self._dish_leaf_node_group.get_device_list(True))

            print "Dishproxy list", self._dish_leaf_node_proxy
            print "health id in Release fun ", self._health_event_id
            #self._dish_leaf_node_proxy[0].unsubscribe_event(self._health_event_id[0])
            #self._dish_leaf_node_proxy[1].unsubscribe_event(self._health_event_id[1])

            '''for leaf in range(0, len(self._health_event_id)):
                print "DishLeafNode proxy :-> ", self._dish_leaf_node_proxy[leaf]
                print "Health Event ID :-> ", self._health_event_id[leaf]
                self._dish_leaf_node_proxy[leaf].unsubscribe_event(self._health_event_id[leaf])'''
            print 'self.testDeviceVsEventID ', self.testDeviceVsEventID

            for dev in self.testDeviceVsEventID:
                dev.unsubscribe_event(self.testDeviceVsEventID[dev])
            self.testDeviceVsEventID = {}
            #
            #     self._dish_leaf_node_proxy[leaf].unsubscribe_event(self._health_event_id[leaf])
            #     print "after unsubscribing"
            self._health_event_id = []
            self._dish_leaf_node_proxy = []
            del self._receptor_id_list[:]

            self._scan_id = ""
            self._sb_id = ""

            self.set_state(DevState.OFF)                                                                                # Set state = OFF
            self._obs_state = 0                                                                                         # set obsState to "IDLE"
            self.set_status("All the receptors are removed from the Subarray node.")
            self.devlogmsg("All the receptors are removed from the Subarray node.", 4)
        except Exception as e:
            print "Exception in ReleaseAllResources command:"
            print e
            print "Dishproxy list", self._dish_leaf_node_proxy
            print "health id in Release fun ", self._health_event_id

            self._read_activity_message = "Exception in ReleaseAllResources command: \n " + str(e)

            argout = []
            self.devlogmsg("Exception occurred in ReleaseAllResources command.", 2)
        return argout

    def is_ReleaseAllResources_allowed(self):
        return self.get_state() not in [DevState.FAULT,DevState.UNKNOWN,DevState.DISABLE,DevState.STANDBY]

    def setHealth (self, evt):
        if (evt.err == False):
            try:
                self._dish_health_state = evt.attr_value.value
                self.dishHealthStateMap[evt.device] = self._dish_health_state
                if (self._dish_health_state == 0):
                    print "Health state of " + str(evt.device) + " :-> OK"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> OK"

                elif (self._dish_health_state == 1):
                    print "Health state of " + str(evt.device) + " :-> DEGRADED"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> DEGRADED"

                elif (self._dish_health_state == 2):
                    print "Health state of " + str(evt.device) + " :-> FAILED"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> FAILED"

                elif (self._dish_health_state == 3):
                    print "Health state of " + str(evt.device) + " :-> UNKNOWN"
                    self._read_activity_message = "Health state of " + str(evt.device) + " :-> UNKNOWN"

                else:
                    print "Dish Health state event returned unknown value! \n", evt
                    self._read_activity_message = "Dish Health state event returned unknown value! \n" + str(evt)

                #Aggregated Health State
                failed = 0
                degraded = 0
                unknown = 0
                ok = 0
                for value in (self.dishHealthStateMap.values()):
                    if value == 2:
                        failed = failed + 1
                        break
                    elif value == 1:
                        self._health_state = 1
                        degraded = degraded + 1
                    elif value == 3:
                        self._health_state = 3
                        unknown = unknown + 1

                    else:
                        self._health_state = 0
                        ok = ok + 1

                if ok == len(self.dishHealthStateMap.values()):
                    self._health_state = 0

                elif failed != 0:
                    self._health_state = 2

                elif degraded != 0:
                    self._health_state = 1

                else:
                    self._health_state = 3

            except Exception as e:
                print "Unexpected error while aggregating Health state!\n", e.message
                self._read_activity_message = "Unexpected error while aggregating Health state!\n" + str(e.message)

                self.devlogmsg("Unexpected error while aggregating Health state.", 2)
        else:
            print "Error event on subscribing HealthState attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing HealthState attribute!\n" + str(evt.errors)
            self.devlogmsg("Error event on subscribing HealthState attribute.", 2)



    # PROTECTED REGION END #    //  SubarrayNode.class_variable

    # -----------------
    # Device Properties
    # -----------------









    DishLeafNodePrefix = device_property(
        dtype='str', default_value="ska_mid/tm_leaf_node/d"
    )

    # ----------
    # Attributes
    # ----------
















    scanID = attribute(
        dtype='str',
    )

    sbID = attribute(
        dtype='str',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )



    receptorIDList = attribute(
        dtype=('uint16',),
        max_dim_x=100,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKASubarray.init_device(self)
        # PROTECTED REGION ID(SubarrayNode.init_device) ENABLED START #

        self.set_state(DevState.INIT)
        self.set_status("Initializing SubarrayNode...")
        self.SkaLevel = 2                                                                                               # set SKALevel to "2"
        self._admin_mode = 0                                                                                            # set adminMode to "ON-LINE"
        self._health_state = 0                                                                                          # set health state to "OK"
        self._obs_state = 0                                                                                             # set obsState to "IDLE"
        self._obs_mode = 0                                                                                              # set obsMode to "IDLE"
        self._simulation_mode = False
        self._scan_id = ""
        self._sb_id = ""
        self._receptor_id_list = []
        self.dishHealthStateMap = {}

        self._dish_leaf_node_group = PyTango.Group("DishLeafNode_Group")
        self._dish_leaf_node_proxy = []
        self._health_event_id = []
        self.testDeviceVsEventID = {}
        self.set_state(DevState.OFF)                                                                                    # Set state = OFF
        self._read_activity_message = "Subarray node is initialized successfully."
        self.set_status("SubarrayNode is initialized successfully.")
        self.devlogmsg("SubarrayNode is initialized successfully.", 4)

        # PROTECTED REGION END #    //  SubarrayNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SubarrayNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SubarrayNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SubarrayNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SubarrayNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        # PROTECTED REGION ID(SubarrayNode.scanID_read) ENABLED START #
        return self._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_sbID(self):
        # PROTECTED REGION ID(SubarrayNode.sbID_read) ENABLED START #
        return self._sb_id
        # PROTECTED REGION END #    //  SubarrayNode.sbID_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    def read_receptorIDList(self):
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

        try:
            print "Input Arguments for Configure command :-> " , argin
            print "Group Definitions during Configure command :-> " ,  self._dish_leaf_node_group.get_device_list()

            self._read_activity_message = "Input Arguments for Configure command :-> " + str(argin)
            self._read_activity_message =  "Group Definitions during Configure command :-> " + str(self._dish_leaf_node_group.get_device_list())

            cmdData = PyTango.DeviceData()
            cmdData.insert(PyTango.DevVarStringArray, argin)
            self._obs_state = 1                                                                                         # set obsState to CONFIGURING when the configuration is started
            self._dish_leaf_node_group.command_inout("Configure", cmdData)
            self._obs_state = 2                                                                                         # set obsState to READY when the configuration is completed
            self._scan_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self._sb_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self.devlogmsg("Configure command invoked on Subarray", 4)
        except Exception as e:
            print "Exception in Configure command:"
            print e

            self._read_activity_message = "Exception in Configure command: \n " + str(e)

            self.devlogmsg("Exception occurred in Configure command.", 2)

        # PROTECTED REGION END #    //  SubarrayNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(SubarrayNode.is_Configure_allowed) ENABLED START #
        return self.get_state() not in [DevState.FAULT,DevState.UNKNOWN,DevState.DISABLE,DevState.STANDBY]
        # PROTECTED REGION END #    //  SubarrayNode.is_Configure_allowed

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SubarrayNode.main) ENABLED START #
    return run((SubarrayNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SubarrayNode.main

if __name__ == '__main__':
    main()
