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

# tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, ApiUtil, DevState
from tango.server import run, DeviceMeta, attribute, command, device_property
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(DishLeafNode.additionnal_import) ENABLED START #
import CONST
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
        """
        This method identifies the Dish mode which is received as an event
        :param evt: dishMode
        :return:
        """
        if evt.err is False:
            try:
                self._dish_mode = evt.attr_value.value
                if self._dish_mode == 0:
                    print CONST.STR_DISH_OFF_MODE
                    self._read_activity_message = CONST.STR_DISH_OFF_MODE
                elif self._dish_mode == 1:
                    print CONST.STR_DISH_STARTUP_MODE
                    self._read_activity_message = CONST.STR_DISH_STARTUP_MODE
                elif self._dish_mode == 2:
                    print CONST.STR_DISH_SHUTDOWN_MODE
                    self._read_activity_message = CONST.STR_DISH_SHUTDOWN_MODE
                elif self._dish_mode == 3:
                    print CONST.STR_DISH_STANDBYLP_MODE
                    self._read_activity_message = CONST.STR_DISH_STANDBYLP_MODE
                elif self._dish_mode == 4:
                    print CONST.STR_DISH_STANDBYFP_MODE
                    self._read_activity_message = CONST.STR_DISH_STANDBYFP_MODE
                elif self._dish_mode == 5:
                    print CONST.STR_DISH_MAINT_MODE
                    self._read_activity_message = CONST.STR_DISH_MAINT_MODE
                elif self._dish_mode == 6:
                    print CONST.STR_DISH_STOW_MODE
                    self._read_activity_message = CONST.STR_DISH_STOW_MODE
                elif self._dish_mode == 7:
                    print CONST.STR_DISH_CONFIG_MODE
                    self._read_activity_message = CONST.STR_DISH_CONFIG_MODE
                elif self._dish_mode == 8:
                    print CONST.STR_DISH_OPERATE_MODE
                    self._read_activity_message = CONST.STR_DISH_OPERATE_MODE
                else:
                    print CONST.STR_DISH_UNKNOWN_MODE, evt
                    self._read_activity_message = CONST.STR_DISH_UNKNOWN_MODE + str(evt)
            except Exception as except_occurred:
                print CONST.ERR_DISH_MODE_CB, except_occurred.message
                self._read_activity_message = CONST.ERR_DISH_MODE_CB\
                                              + str(except_occurred.message)
                self.devlogmsg(CONST.ERR_DISH_MODE_CB, 2)
        else:
            print CONST.ERR_ON_SUBS_DISH_MODE_ATTR, evt.errors
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_MODE_ATTR + str(evt.errors)
            self.devlogmsg(CONST.ERR_ON_SUBS_DISH_MODE_ATTR, 2)

    def dishPointingStateCallback(self, evt):
        """
        This method identifies the pointing state of the Dish which is received as an event
        :param evt: dishPointingState
        :return:
        """
        if evt.err is False:
            try:
                self._pointing_state = evt.attr_value.value
                if self._pointing_state == 0:
                    print CONST.STR_DISH_POINT_STATE_READY
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_READY
                elif self._pointing_state == 1:
                    print CONST.STR_DISH_POINT_STATE_SLEW
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_SLEW
                elif self._pointing_state == 2:
                    print CONST.STR_DISH_POINT_STATE_TRACK
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_TRACK
                elif self._pointing_state == 3:
                    print CONST.STR_DISH_POINT_STATE_SCAN
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_SCAN
                else:
                    print CONST.STR_DISH_POINT_STATE_UNKNOWN, evt
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_UNKNOWN + str(evt)
            except Exception as except_occurred:
                print CONST.ERR_DISH_POINT_STATE_CB, except_occurred.message
                self._read_activity_message = CONST.ERR_DISH_POINT_STATE_CB\
                                              + str(except_occurred.message)
                self.devlogmsg(CONST.ERR_DISH_POINT_STATE_CB, 2)
        else:
            print CONST.ERR_ON_SUBS_DISH_POINT_ATTR, evt.errors
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_POINT_ATTR + str(evt.errors)
            self.devlogmsg(CONST.ERR_ON_SUBS_DISH_POINT_ATTR, 2)

    def dishHealthStateCallback(self, evt):
        """
        This method identifies the heath state of the Dish which is received as an event
        :param self:
        :param evt: dishHealthState
        :return:
        """
        if evt.err is False:
            try:
                self._health_state_dish = evt.attr_value.value
                if self._health_state_dish == 0:
                    print CONST.STR_DISH_HEALTH_STATE_OK
                    self._read_activity_message = CONST.STR_DISH_HEALTH_STATE_OK
                elif self._health_state_dish == 1:
                    print CONST.STR_DISH_HEALTH_STATE_DEGRADED
                    self._read_activity_message = CONST.STR_DISH_HEALTH_STATE_DEGRADED
                elif self._health_state_dish == 2:
                    print CONST.STR_DISH_HEALTH_STATE_FAILED
                    self._read_activity_message = CONST.STR_DISH_HEALTH_STATE_FAILED
                elif self._health_state_dish == 3:
                    print CONST.STR_DISH_HEALTH_STATE_UNKNOWN
                    self._read_activity_message = CONST.STR_DISH_HEALTH_STATE_UNKNOWN
                else:
                    print CONST.STR_DISH_HEALTH_STATE_ERR, self._health_state_dish, "\n", evt
                    self._read_activity_message = CONST.STR_DISH_HEALTH_STATE_ERR\
                                                  + str(self._health_state_dish) + "\n" + str(evt)
            except Exception as except_occurred:
                print CONST.ERR_DISH_HEALTH_STATE_CB, except_occurred.message
                self._read_activity_message = CONST.ERR_DISH_HEALTH_STATE_CB\
                                              + str(except_occurred.message)
                self.devlogmsg(CONST.ERR_DISH_HEALTH_STATE_CB, 2)
        else:
            print CONST.ERR_SUBSR_DISH_HEALTH_STATE, evt.errors
            self._read_activity_message = CONST.ERR_SUBSR_DISH_HEALTH_STATE\
                                          + str(evt.errors)
            self.devlogmsg(CONST.ERR_SUBSR_DISH_HEALTH_STATE, 2)

    def dishCapturingCallback(self, evt):
        """
        This method identifies whether the Dish is capturing data by comparing the received event
        :param evt: dishCapturing status
        :return:
        """
        if evt.err is False:
            try:
                self._dish_capturing = evt.attr_value.value
                if self._dish_capturing is True:
                    print CONST.STR_DISH_CAPTURING_TRUE
                    self._read_activity_message = CONST.STR_DISH_CAPTURING_TRUE
                elif self._dish_capturing is False:
                    print CONST.STR_DISH_CAPTURING_FALSE
                    self._read_activity_message = CONST.STR_DISH_CAPTURING_FALSE
                else:
                    print CONST.STR_DISH_CAPTURING_UNKNOWN, evt
                    self._read_activity_message = CONST.STR_DISH_CAPTURING_UNKNOWN + str(evt)
            except Exception as except_occurred:
                print CONST.ERR_DISH_CAPTURING_CB, except_occurred.message
                self._read_activity_message = CONST.ERR_DISH_CAPTURING_CB\
                                              + str(except_occurred.message)
                self.devlogmsg(CONST.ERR_DISH_CAPTURING_CB, 2)
        else:
            print CONST.ERR_SUBSR_CAPTURING_ATTR, evt.errors
            self._read_activity_message = CONST.ERR_SUBSR_CAPTURING_ATTR + str(evt.errors)
            self.devlogmsg(CONST.ERR_SUBSR_CAPTURING_ATTR, 2)

    def dishAchievedPointingCallback(self, evt):
        """
        This method identifies whether the Dish has achieved pointing.
        :param evt: dishAchievedPointing
        :return:
        """
        if evt.err is False:
            try:
                self._achieved_pointing = evt.attr_value.value
                print CONST.STR_ACHIEVED_POINTING, self._achieved_pointing
                self._read_activity_message = CONST.STR_ACHIEVED_POINTING\
                                              + str(self._achieved_pointing)

            except Exception as except_occurred:
                print CONST.ERR_DISH_ACHVD_POINT, except_occurred.message
                self._read_activity_message = CONST.ERR_DISH_ACHVD_POINT\
                                              + str(except_occurred.message)
                self.devlogmsg(CONST.ERR_DISH_ACHVD_POINT, 2)
        else:
            print CONST.ERR_ON_SUBS_DISH_ACHVD_ATTR, evt.errors
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_ACHVD_ATTR + str(evt.errors)
            self.devlogmsg(CONST.ERR_ON_SUBS_DISH_ACHVD_ATTR, 2)

    def dishDesiredPointingCallback(self, evt):
        """
         This method identifies whether the Dish has reached the desired pointing.
        :param evt: dishDesiredPointing
        :return:
        """
        if evt.err is False:
            try:
                self._desired_pointing = evt.attr_value.value
                print CONST.STR_DESIRED_POINTING, self._desired_pointing
                self._read_activity_message = CONST.STR_DESIRED_POINTING\
                                              + str(self._desired_pointing)

            except Exception as except_occurred:
                print CONST.ERR_DISH_DESIRED_POINT, except_occurred.message
                self._read_activity_message = CONST.ERR_DISH_DESIRED_POINT\
                                              + str(except_occurred.message)
                self.devlogmsg(CONST.ERR_DISH_DESIRED_POINT, 2)
        else:
            print CONST.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR, evt.errors
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR\
                                          + str(evt.errors)
            self.devlogmsg(CONST.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR, 2)

    def commandCallback(self, event):
        """
        This method checks whether the command has been successfully invoked.
        :param event: status of the command invoked (true or false)
        :return:
        """
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                # error = tango.DevFailed(*event.errors)
                # tango.Except.print_exception(error)

                print CONST.ERR_INVOKING_CMD + event.cmd_name + "\n" + str(event.errors)
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name)\
                                              + "\n" + str(event.errors)


                self.devlogmsg(log, 2)
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self.devlogmsg(log, 4)
        except Exception as except_occurred:
            print CONST.ERR_EXCEPT_CMD_CB, except_occurred
            self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            self.devlogmsg(CONST.ERR_EXCEPT_CMD_CB, 2)




    # PROTECTED REGION END #    //  DishLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------







    DishMasterFQDN = device_property(
        dtype='str', default_value="tango://apurva-pc:10000/mid_d0001/elt/master"
    )

    # ----------
    # Attributes
    # ----------











    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    dishHealthState = attribute(name="dishHealthState", label="dishHealthState", forwarded=True)
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """
        This method initializes the attributes. It subscribes to the different events of the Dish
        Master.
        :return:
        """
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(DishLeafNode.init_device) ENABLED START #
        print CONST.STR_INIT_LEAF_NODE
        self._read_activity_message = CONST.STR_INIT_LEAF_NODE
        self.SkaLevel = 3
        try:
            print CONST.STR_DISHMASTER_FQN, self.DishMasterFQDN
            self._read_activity_message = CONST.STR_DISHMASTER_FQN + str(self.DishMasterFQDN)
            self._dish_proxy = DeviceProxy(self.DishMasterFQDN)   #Creating proxy to the DishMaster
        except Exception as except_occurred:
            print CONST.ERR_IN_CREATE_PROXY_DM, except_occurred
            self._read_activity_message = CONST.ERR_IN_CREATE_PROXY_DM + str(except_occurred)
            self.set_state(DevState.FAULT)

        self._admin_mode = 0                                    #Setting adminMode to "ONLINE"
        self._health_state = 0                                  #Setting healthState to "OK"
        self._simulation_mode = False                           #Enabling the simulation mode

        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        print CONST.STR_SETTING_CB_MODEL, ApiUtil.instance().get_asynch_cb_sub_model()
        self._read_activity_message = CONST.STR_SETTING_CB_MODEL\
                                      + str(ApiUtil.instance().get_asynch_cb_sub_model())

        # Subscribing to DishMaster Attributes

        try:
            self._dish_proxy.subscribe_event(CONST.EVT_DISH_MODE, EventType.CHANGE_EVENT,
                                             self.dishModeCallback, stateless=True)
            self._dish_proxy.subscribe_event(CONST.EVT_DISH_POINTING_STATE, EventType.CHANGE_EVENT,
                                             self.dishPointingStateCallback, stateless=True)
            self._dish_proxy.subscribe_event(CONST.EVT_DISH_CAPTURING, EventType.CHANGE_EVENT,
                                             self.dishCapturingCallback, stateless=True)
            self._dish_proxy.subscribe_event(CONST.EVT_ACHVD_POINT, EventType.CHANGE_EVENT,
                                             self.dishAchievedPointingCallback, stateless=True)
            self._dish_proxy.subscribe_event(CONST.EVT_DESIRED_POINT, EventType.CHANGE_EVENT,
                                             self.dishDesiredPointingCallback, stateless=True)
            self.set_state(DevState.ON)
            self.set_status(CONST.STR_DISH_INIT_SUCCESS)
            self.devlogmsg(CONST.STR_DISH_INIT_SUCCESS, 4)

        except Exception as except_occurred:
            print CONST.ERR_SUBS_DISH_ATTR, except_occurred
            self._read_activity_message = CONST.ERR_SUBS_DISH_ATTR + str(except_occurred)
            self.set_state(DevState.FAULT)
            self.set_status(CONST.ERR_DISH_INIT)
            self.devlogmsg(CONST.ERR_DISH_INIT, 2)



        # PROTECTED REGION END #    //  DishLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(DishLeafNode.always_executed_hook) ENABLED START #
        """ This method is an internal construct of TANGO """
        pass
        # PROTECTED REGION END #    //  DishLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(DishLeafNode.delete_device) ENABLED START #
        """ This method is an internal construct of TANGO """
        pass
        # PROTECTED REGION END #    //  DishLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(DishLeafNode.activityMessage_read) ENABLED START #
        """
        This is a getter method for the activityMessage attribute
        :return:
        """
        return self._read_activity_message
        # PROTECTED REGION END #    //  DishLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(DishLeafNode.activityMessage_write) ENABLED START #
        """
        This is a setter method for the activityMessage attribute
        :param value: activityMessage
        :return:
        """
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
        """
        This command is used to stow the receptor.
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_SET_STOW_MODE, self.commandCallback)

        except Exception as except_occurred:
            print CONST.ERR_EXE_STOW_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_STOW_CMD + str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_STOW_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetStowMode

    @command(
    )
    @DebugIt()
    def SetStandByLPMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStandByLPMode) ENABLED START #
        """
        This command is to bring the Telescope into a STANDBY state (i.e. Low Power State)
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_SET_STANDBYLP_MODE,
                                                  self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_STANDBYLP_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_STANDBYLP_CMD, str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_STANDBYLP_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetStandByLPMode

    @command(
    )
    @DebugIt()
    def SetOperateMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetOperateMode) ENABLED START #
        """
        This command triggers the Dish to transition to the Operate Dish Element mode.
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_SET_OPERATE_MODE, self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_SET_OPER_MODE_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_SET_OPER_MODE_CMD, except_occurred
            self.devlogmsg(CONST.ERR_EXE_SET_OPER_MODE_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetOperateMode

    @command(
        dtype_in='str',
        doc_in="Timestamp",
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Scan) ENABLED START #
        """
        Command the Dish to start the Scan.
        :param argin: timestamp
        :return:
        """
        try:
            print CONST.STR_IN_SCAN
            self._dish_proxy.command_inout_asynch(CONST.CMD_DISH_SCAN, argin, self.commandCallback)
            print CONST.STR_OUT_SCAN
        except Exception as except_occurred:
            print CONST.ERR_EXE_SCAN_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_SCAN_CMD, except_occurred
            self.devlogmsg(CONST.ERR_EXE_SCAN_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.Scan

    @command(
        dtype_in='str',
        doc_in="Timestamp",
    )
    @DebugIt()
    def EndScan(self, argin):
        # PROTECTED REGION ID(DishLeafNode.EndScan) ENABLED START #
        """
        Command the Dish to stop the Scan.
        :param argin:
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_STOP_CAPTURE,
                                                  argin, self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_END_SCAN_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_END_SCAN_CMD+ str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_END_SCAN_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.EndScan

    @command(
        dtype_in=('str',),
        doc_in="Pointing parameter of Dish",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Configure) ENABLED START #
        """
        Command to configure Dish. Configuration includes setting pointing coordinates of Dish
        for a given observation.
        :param argin: TBD
        :return:
        """
        try:
            argin1 = [float(argin[0]), float(argin[1])]
            spectrum = [0]
            spectrum.extend((argin1))
            self._dish_proxy.desiredPointing = spectrum
            self._dish_proxy.command_inout_asynch(CONST.CMD_DISH_SLEW, "0", self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_CONFIGURE_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_CONFIGURE_CMD +  str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_CONFIGURE_CMD, 2)

        # PROTECTED REGION END #    //  DishLeafNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_Configure_allowed) ENABLED START #
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.INIT, DevState.ALARM, DevState.DISABLE,
                                        DevState.OFF, DevState.STANDBY]
        # PROTECTED REGION END #    //  DishLeafNode.is_Configure_allowed

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
    )
    @DebugIt()
    def StartCapture(self, argin):
        # PROTECTED REGION ID(DishLeafNode.StartCapture) ENABLED START #
        """
        This method sends the command to Start capture on the configured band.
        Command only valid in SPFRx Data_Capture mode.
        :param argin: timestamp
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_START_CAPTURE,
                                                  argin, self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_START_CAPTURE_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_START_CAPTURE_CMD\
                                          + str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_START_CAPTURE_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.StartCapture

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
    )
    @DebugIt()
    def StopCapture(self, argin):
        # PROTECTED REGION ID(DishLeafNode.StopCapture) ENABLED START #
        """
        This method sends the command to Stop capture on the configured band.
        :param argin: timestamp
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_STOP_CAPTURE,
                                                  argin, self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_STOP_CAPTURE_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_STOP_CAPTURE_CMD + str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_STOP_CAPTURE_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.StopCapture

    @command(
    )
    @DebugIt()
    def SetStandbyFPMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStandbyFPMode) ENABLED START #
        """
        This command triggers the Dish to transition to the STANDBY-FP Dish Element Mode
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_SET_STANDBYFP_MODE,
                                                  self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_STANDBYFP_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_STANDBYFP_CMD + str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_STANDBYFP_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.SetStandbyFPMode

    @command(
        dtype_in='str',
        doc_in="Timestamp at which command should be executed.",
    )
    @DebugIt()
    def Slew(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Slew) ENABLED START #
        """
        This method sends the slew command to the Dish master. Dish moves to the commanded
        pointing angle at the maximum speed, as defined by specified slew rate.
        :param argin: timestamp
        :return:
        """
        try:
            self._dish_proxy.command_inout_asynch(CONST.CMD_DISH_SLEW, argin, self.commandCallback)
        except Exception as except_occurred:
            print CONST.ERR_EXE_SLEW_CMD, except_occurred
            self._read_activity_message = CONST.ERR_EXE_SLEW_CMD + str(except_occurred)
            self.devlogmsg(CONST.ERR_EXE_SLEW_CMD, 2)
        # PROTECTED REGION END #    //  DishLeafNode.Slew

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(DishLeafNode.main) ENABLED START #
    """
    The main method runs the DishLeafNode
    :param args:
    :param kwargs:
    :return:
    """
    return run((DishLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  DishLeafNode.main

if __name__ == '__main__':
    main()
