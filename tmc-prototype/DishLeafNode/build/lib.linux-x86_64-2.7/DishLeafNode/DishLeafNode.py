# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

A Leaf control node for DishMaster.
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
# PROTECTED REGION ID(DishLeafNode.additionnal_import) ENABLED START #
from tango import DeviceProxy, DevState, EventType, utils, DeviceData, ApiUtil
from tango.server import attribute
import traceback


# PROTECTED REGION END #    //  DishLeafNode.additionnal_import

__all__ = ["DishLeafNode", "main"]


class DishLeafNode(SKABaseDevice):
    """
    A Leaf control node for DishMaster.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(DishLeafNode.class_variable) ENABLED START #
    #_dish_proxy = device_property("DishMasterFQDN")

    def dishModeCallback(self, evt):

        if (evt.err==False):
            try:
                self._dish_mode = evt.attr_value.value
                if(self._dish_mode == 0):
                    print "Dish Mode :-> OFF"
                    self._read_activity_message = "Dish Mode :-> OFF"
                elif (self._dish_mode == 1):
                    print "Dish Mode :-> STARTUP"
                    self._read_activity_message = "Dish Mode :-> STARTUP"
                elif (self._dish_mode == 2):
                    print "Dish Mode :->  SHUTDOWN"
                    self._read_activity_message = "Dish Mode :->  SHUTDOWN"
                elif (self._dish_mode == 3):
                    print "Dish Mode :->  STANDBY-LP"
                    self._read_activity_message = "Dish Mode :->  STANDBY-LP"
                elif (self._dish_mode == 4):
                    print "Dish Mode :-> STANDBY-FP"
                    self._read_activity_message = "Dish Mode :-> STANDBY-FP"
                elif (self._dish_mode == 5):
                    print "Dish Mode :-> MAINTENANCE"
                    self._read_activity_message = "Dish Mode :-> MAINTENANCE"
                elif (self._dish_mode == 6):
                    print "Dish Mode :-> STOW"
                    self._read_activity_message = "Dish Mode :-> STOW"
                elif (self._dish_mode == 7):
                    print "Dish Mode :-> CONFIG"
                    self._read_activity_message = "Dish Mode :-> CONFIG"
                elif (self._dish_mode == 8):
                    print "Dish Mode :-> OPERATE"
                    self._read_activity_message = "Dish Mode :-> OPERATE"
                else:
                    print "Dish Mode :-> UNKNOWN!\n", evt
                    self._read_activity_message = "Dish Mode :-> UNKNOWN!\n" + str(evt)
            except Exception as e:
                print "Unexpected error in DishModeCallback!\n", e.message
                self._read_activity_message = "Unexpected error in DishModeCallback!\n" +  str(e.message)
                self.devlogmsg("Unexpected error in DishModeCallback!", 2)
        else:
            print "Error event on subscribing DishMode attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing DishMode attribute!\n" + str(evt.errors)
            self.devlogmsg("Error event on subscribing DishMode attribute!", 2)

    def dishPointingStateCallback(self, evt):

        if (evt.err==False):
            try:
                self._pointing_state = evt.attr_value.value
                if(self._pointing_state == 0):
                    print "Dish Pointing State :-> READY"
                    self._read_activity_message = "Dish Pointing State :-> READY"
                elif (self._pointing_state == 1):
                    print "Dish Pointing State :-> SLEWING"
                    self._read_activity_message = "Dish Pointing State :-> SLEWING"
                elif (self._pointing_state == 2):
                    print "Dish Pointing State :-> TRACKING"
                    self._read_activity_message = "Dish Pointing State :-> TRACKING"
                elif (self._pointing_state == 3):
                    print "Dish Pointing State :-> SCANNING"
                    self._read_activity_message = "Dish Pointing State :-> SCANNING"
                else:
                    print "Dish is in UNKNOWN pointing state!\n", evt
                    self._read_activity_message = "Dish is in UNKNOWN pointing state!\n" + str(evt)
            except Exception as e:
                print "Unexpected error in DishPointingStateCallback!\n", e.message
                self._read_activity_message = "Unexpected error in DishPointingStateCallback!\n" + str(e.message)
                self.devlogmsg("Unexpected error in DishPointingStateCallback!", 2)
        else:
            print "Error event on subscribing PointingState attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing PointingState attribute!\n" + str(evt.errors)
            self.devlogmsg("Error event on subscribing PointingState attribute!", 2)

    def dishHealthStateCallback(self, evt):

        if (evt.err==False):
            try:
                self._health_state_dish = evt.attr_value.value
                if(self._health_state_dish == 0):
                    print "Dish Health state :-> OK"
                    self._read_activity_message = "Dish Health state :-> OK"
                elif (self._health_state_dish == 1):
                    print "Dish Health state :-> DEGRADED"
                    self._read_activity_message = "Dish Health state :-> DEGRADED"
                elif (self._health_state_dish == 2):
                    print "Dish Health state :-> FAILED"
                    self._read_activity_message = "Dish Health state :-> FAILED"
                elif (self._health_state_dish == 3):
                    print "Dish Health state :-> UNKNOWN"
                    self._read_activity_message = "Dish Health state :-> UNKNOWN"
                else:
                    print "Error: Dish Health state :-> ", self._health_state_dish, "\n", evt
                    self._read_activity_message = "Error: Dish Health state :-> " + str(self._health_state_dish) + "\n" + str(evt)
            except Exception as e:
                print "Unexpected error in DishHealthStateCallback!\n", e.message
                self._read_activity_message = "Unexpected error in DishHealthStateCallback!\n" + str(e.message)
                self.devlogmsg("Unexpected error in DishHealthStateCallback!", 2)
        else:
            print "Error event on subscribing HealthState attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing HealthState attribute!\n" + str(evt.errors)
            self.devlogmsg("Error event on subscribing HealthState attribute!", 2)

    def dishCapturingCallback(self, evt):

        if (evt.err==False):
            try:
                self._dish_capturing = evt.attr_value.value
                if(self._dish_capturing == True):
                    print "Dish data capturing :-> TRUE"
                    self._read_activity_message = "Dish data capturing :-> TRUE"
                elif (self._dish_capturing == False):
                    print "Dish data capturing :-> FALSE"
                    self._read_activity_message = "Dish data capturing :-> FALSE"
                else:
                    print "Dish date capturing :-> UNKNOWN!\n", evt
                    self._read_activity_message = "Dish date capturing :-> UNKNOWN!\n" + str(evt)
            except Exception as e:
                print "Unexpected error in DishCapturingCallback!\n", e.message
                self._read_activity_message = "Unexpected error in DishCapturingCallback!\n" + str(e.message)
                self.devlogmsg("Unexpected error in DishCapturingCallback!", 2)
        else:
            print "Error event on subscribing Capturing attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing Capturing attribute!\n" + str(evt.errors)
            self.devlogmsg("Error event on subscribing Capturing attribute!", 2)

    def dishAchievedPointingCallback(self, evt):

        if (evt.err==False):
            try:
                self._achieved_pointing = evt.attr_value.value
                print "Achieved Pointing :-> ", self._achieved_pointing
                self._read_activity_message = "Achieved Pointing :-> " + str(self._achieved_pointing)

            except Exception as e:
                print "Unexpected error in DishAchievedPointingCallback!\n", e.message
                self._read_activity_message = "Unexpected error in DishAchievedPointingCallback!\n" + str(e.message)
                self.devlogmsg("Unexpected error in DishAchievedPointingCallback!", 2)
        else:
            print "Error event on subscribing AchievedPointing attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing AchievedPointing attribute!\n" + str(evt.errors)
            self.devlogmsg("Error event on subscribing AchievedPointing attribute!", 2)

    def dishDesiredPointingCallback(self, evt):

        if (evt.err==False):
            try:
                self._desired_pointing = evt.attr_value.value
                print "Desired Pointing :-> ", self._desired_pointing
                self._read_activity_message = "Desired Pointing :-> " + str(self._desired_pointing)

            except Exception as e:
                print "Unexpected error in DishDesiredPointingCallback!\n", e.message
                self._read_activity_message = "Unexpected error in DishDesiredPointingCallback!\n" +  str(e.message)
                self.devlogmsg("Unexpected error in DishDesiredPointingCallback!", 2)
        else:
            print "Error event on subscribing DesiredPointing attribute!\n", evt.errors
            self._read_activity_message = "Error event on subscribing DesiredPointing attribute!\n" +  str(evt.errors)
            self.devlogmsg("Error event on subscribing DesiredPointing attribute!", 2)

    def commandCallback(self, event):
        try:
            if event.err:
                log = "Error in invoking command:" + event.cmd_name
                # error = PyTango.DevFailed(*event.errors)
                # PyTango.Except.print_exception(error)

                print "Error in invoking command: " + event.cmd_name + "\n" + str(event.errors)
                self._read_activity_message = "Error in invoking command:" + str(event.cmd_name) + "\n" + str(event.errors)


                self.devlogmsg(log, 2)
            else:
                log = "Command :->" + event.cmd_name + "invoked successfully."
                self.devlogmsg(log, 4)
        except Exception as e:
            print "Exception in CommandCallback!: \n", e
            self._read_activity_message = "Exception in CommandCallback!: \n" + str(e)
            self.devlogmsg("Exception in CommandCallback!", 2)




    # PROTECTED REGION END #    //  DishLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------







    DishMasterFQDN = device_property(
        dtype='str',
        mandatory=True
    )

    # ----------
    # Attributes
    # ----------











    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    dishHealthState = attribute(name="dishHealthState", label="dishHealthState",
        forwarded=True
    )
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(DishLeafNode.init_device) ENABLED START #
        print "Initializing Leaf Node..."
        self._read_activity_message = "Initializing Leaf Node..."
        self.SkaLevel=3
        try:
            self._dish_proxy = DeviceProxy(self.DishMasterFQDN)     #Creating proxy to the DishMaster
        except Exception as e:
            print "Exception occurred while creating proxy to Dish Master!\n", e
            self._read_activity_message = "Exception occurred while creating proxy to Dish Master!\n" + str(e)
            self.set_state(DevState.FAULT)

        self._admin_mode = 0                                    #Setting adminMode to "ONLINE"
        self._health_state = 0                                  #Setting healthState to "OK"
        self._simulation_mode = False                           #Enabling the simulation mode

        ApiUtil.instance().set_asynch_cb_sub_model(PyTango.cb_sub_model.PUSH_CALLBACK)
        print "Setting CallBack Model as :-> ", ApiUtil.instance().get_asynch_cb_sub_model()
        self._read_activity_message = "Setting CallBack Model as :-> " + str(ApiUtil.instance().get_asynch_cb_sub_model())

        # Subscribing to DishMaster Attributes

        try:
            self._dish_proxy.subscribe_event("dishMode", EventType.CHANGE_EVENT, self.dishModeCallback, stateless=True)
            self._dish_proxy.subscribe_event("pointingState", EventType.CHANGE_EVENT, self.dishPointingStateCallback, stateless=True)
            #self._dish_proxy.subscribe_event("healthState",EventType.CHANGE_EVENT, self.dishHealthStateCallback, stateless=True)
            self._dish_proxy.subscribe_event("capturing",EventType.CHANGE_EVENT, self.dishCapturingCallback, stateless=True)
            self._dish_proxy.subscribe_event("achievedPointing", EventType.CHANGE_EVENT, self.dishAchievedPointingCallback, stateless=True)
            self._dish_proxy.subscribe_event("desiredPointing", EventType.CHANGE_EVENT, self.dishDesiredPointingCallback, stateless=True)
            self.set_state(DevState.ON)
            self.set_status("Dish Leaf Node initialized successfully. Ready to accept commands!")
            self.devlogmsg("Dish Leaf Node initialized successfully.", 4)

        except Exception as e:
            print "Exception occurred while subscribing to Dish attributes", e.message
            self._read_activity_message = "Exception occurred while subscribing to Dish attributes" + str(e.message)
            self.set_state(DevState.FAULT)
            self.set_status("Error occured in Dish Leaf Node initialization!")
            self.devlogmsg("Error occured in Dish Leaf Node initialization!", 2)



        # PROTECTED REGION END #    //  DishLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(DishLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  DishLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(DishLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  DishLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(DishLeafNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  DishLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(DishLeafNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  DishLeafNode.activityMessage_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def SetStowMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStowMode) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("SetStowMode", self.commandCallback)

        except Exception as e:
            print "Exception in SetStowMode command: \n" , e
            self._read_activity_message = "Exception in SetStowMode command: \n" + str(e)
            self.devlogmsg("Exception occurred in SetStowMode command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetStowMode

    @command(
    )
    @DebugIt()
    def SetStandByLPMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStandByLPMode) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("SetStandByLPMode", self.commandCallback)
        except Exception as e:
            print "Exception in SetStandByLPMode command:\n", e
            self._read_activity_message = "Exception in SetStandByLPMode command:\n", str(e)
            self.devlogmsg("Exception occurred in SetStandByLPMode command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetStandByLPMode

    @command(
    )
    @DebugIt()
    def SetOperateMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetOperateMode) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("SetOperateMode", self.commandCallback)
        except Exception as e:
            print "Exception in SetOperateMode command:\n", e
            self._read_activity_message = "Exception in SetOperateMode command:\n", e
            self.devlogmsg("Exception occurred in SetOperateMode command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetOperateMode

    @command(
    dtype_in='str', 
    doc_in="Timestamp", 
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Scan) ENABLED START #
        try:
            print "in scan"
            self._dish_proxy.command_inout_asynch("Scan", argin, self.commandCallback)
            print "out scan"
        except Exception as e:
            print "Exception in Scan command:", e
            self._read_activity_message = "Exception in Scan command:", e
            self.devlogmsg("Exception occurred in Scan command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.Scan

    @command(
    dtype_in='str', 
    doc_in="Timestamp", 
    )
    @DebugIt()
    def EndScan(self, argin):
        # PROTECTED REGION ID(DishLeafNode.EndScan) ENABLED START #

        try:
            self._dish_proxy.command_inout_asynch("StopCapture", argin, self.commandCallback)
        except Exception as e:
            print "Exception in EndScan command:\n", e
            self._read_activity_message = "Exception in EndScan command:\n"+ str(e)
            self.devlogmsg("Exception occurred in EndScan command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.EndScan

    @command(
    dtype_in=('str',), 
    doc_in="Pointing parameter of Dish", 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Configure) ENABLED START #

        try:
            argin1 = [float(argin[0]) , float(argin[1])]
            spectrum = [0]
            spectrum.extend((argin1))
            self._dish_proxy.desiredPointing = spectrum
            self._dish_proxy.command_inout_asynch("Slew", "0",  self.commandCallback)
        except Exception as e:
            print "Exception in Configure command:", e
            self._read_activity_message = "Exception in Configure command:" +  str(e)
            self.devlogmsg("Exception occurred in Configure command.", 2)

        # PROTECTED REGION END #    //  DishLeafNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_Configure_allowed) ENABLED START #
        return self.get_state() not in [DevState.INIT,DevState.ALARM,DevState.DISABLE,DevState.OFF,DevState.STANDBY]
        # PROTECTED REGION END #    //  DishLeafNode.is_Configure_allowed

    @command(
    dtype_in='str', 
    doc_in="The timestamp indicates the time, in UTC, at which command execution should start.", 
    )
    @DebugIt()
    def StartCapture(self, argin):
        # PROTECTED REGION ID(DishLeafNode.StartCapture) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("StartCapture", argin, self.commandCallback)
        except Exception as e:
            print "Exception in StartCapture command:", e
            self._read_activity_message = "Exception in StartCapture command:" + str(e)
            self.devlogmsg("Exception occurred in StartCapture command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.StartCapture

    @command(
    dtype_in='str', 
    doc_in="The timestamp indicates the time, in UTC, at which command execution should start.", 
    )
    @DebugIt()
    def StopCapture(self, argin):
        # PROTECTED REGION ID(DishLeafNode.StopCapture) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("StopCapture", argin, self.commandCallback)
        except Exception as e:
            print "Exception in StopCapture command:", e
            self._read_activity_message = "Exception in StopCapture command:"+ str(e)
            self.devlogmsg("Exception occurred in StopCapture command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.StopCapture

    @command(
    )
    @DebugIt()
    def SetStandbyFPMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStandbyFPMode) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("SetStandbyFPMode", self.commandCallback)
        except Exception as e:
            print "Exception in SetStandbyFPMode command:\n", e
            self._read_activity_message = "Exception in SetStandbyFPMode command:\n" + str(e)
            self.devlogmsg("Exception occurred in SetStandbyFPMode command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetStandbyFPMode

    @command(
    dtype_in='str', 
    doc_in="Timestamp at which command should be executed.", 
    )
    @DebugIt()
    def Slew(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Slew) ENABLED START #
        try:
            self._dish_proxy.command_inout_asynch("Slew", argin, self.commandCallback)
        except Exception as e:
            print "Exception in Slew command:", e
            self._read_activity_message = "Exception in Slew command:"+ str(e)
            self.devlogmsg("Exception occurred in Slew command.", 2)
        # PROTECTED REGION END #    //  DishLeafNode.Slew

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(DishLeafNode.main) ENABLED START #
    return run((DishLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  DishLeafNode.main

if __name__ == '__main__':
    main()
