# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
A Leaf control node for DishMaster.
"""
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/DishLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
# PROTECTED REGION ID(DishLeafNode.additionnal_import) ENABLED START #
# PyTango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType
from tango.server import run, DeviceMeta, command, device_property, attribute
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice

# Additional import
# PROTECTED REGION ID(DishLeafNode.additionnal_import) ENABLED START #
import threading
import CONST
from future.utils import with_metaclass
import math
import katpoint
import re
import datetime
import time
# PROTECTED REGION END #    //  DishLeafNode.additionnal_import

__all__ = ["DishLeafNode", "main"]

class DishLeafNode(with_metaclass(DeviceMeta, SKABaseDevice)):
#class DishLeafNode(SKABaseDevice):
    """
    A Leaf control node for DishMaster.
    """

    # PROTECTED REGION ID(DishLeafNode.class_variable) ENABLED START #
    def dishModeCallback(self, evt):
        """
        Retrieves the subscribed dishMode attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on dishMode attribute.

        :return: None

        """
        if evt.err is False:
            try:
                self._dish_mode = evt.attr_value.value
                if self._dish_mode == 0:
                    print(CONST.STR_DISH_OFF_MODE)
                    self._read_activity_message = CONST.STR_DISH_OFF_MODE
                elif self._dish_mode == 1:
                    print(CONST.STR_DISH_STARTUP_MODE)
                    self._read_activity_message = CONST.STR_DISH_STARTUP_MODE
                elif self._dish_mode == 2:
                    print(CONST.STR_DISH_SHUTDOWN_MODE)
                    self._read_activity_message = CONST.STR_DISH_SHUTDOWN_MODE
                elif self._dish_mode == 3:
                    print(CONST.STR_DISH_STANDBYLP_MODE)
                    self._read_activity_message = CONST.STR_DISH_STANDBYLP_MODE
                elif self._dish_mode == 4:
                    print(CONST.STR_DISH_STANDBYFP_MODE)
                    self._read_activity_message = CONST.STR_DISH_STANDBYFP_MODE
                elif self._dish_mode == 5:
                    print(CONST.STR_DISH_MAINT_MODE)
                    self._read_activity_message = CONST.STR_DISH_MAINT_MODE
                elif self._dish_mode == 6:
                    print(CONST.STR_DISH_STOW_MODE)
                    self._read_activity_message = CONST.STR_DISH_STOW_MODE
                elif self._dish_mode == 7:
                    print(CONST.STR_DISH_CONFIG_MODE)
                    self._read_activity_message = CONST.STR_DISH_CONFIG_MODE
                elif self._dish_mode == 8:
                    print(CONST.STR_DISH_OPERATE_MODE)
                    self._read_activity_message = CONST.STR_DISH_OPERATE_MODE
                else:
                    print(CONST.STR_DISH_UNKNOWN_MODE, evt)
                    self._read_activity_message = CONST.STR_DISH_UNKNOWN_MODE + str(evt)
            except Exception as except_occurred:
                print(CONST.ERR_DISH_MODE_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_DISH_MODE_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_DISH_MODE_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_DISH_MODE_ATTR, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_MODE_ATTR + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_DISH_MODE_ATTR, int(tango.LogLevel.LOG_ERROR))

    def dishPointingStateCallback(self, evt):
        """
        Retrieves the subscribed pointingState attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on pointingState attribute.

        :return: None

        """
        if evt.err is False:
            try:
                self._pointing_state = evt.attr_value.value
                if self._pointing_state == 0:
                    print(CONST.STR_DISH_POINT_STATE_READY)
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_READY
                elif self._pointing_state == 1:
                    print(CONST.STR_DISH_POINT_STATE_SLEW)
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_SLEW
                elif self._pointing_state == 2:
                    print(CONST.STR_DISH_POINT_STATE_TRACK)
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_TRACK
                elif self._pointing_state == 3:
                    print(CONST.STR_DISH_POINT_STATE_SCAN)
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_SCAN
                else:
                    print(CONST.STR_DISH_POINT_STATE_UNKNOWN, evt)
                    self._read_activity_message = CONST.STR_DISH_POINT_STATE_UNKNOWN + str(evt)
            except Exception as except_occurred:
                print(CONST.ERR_DISH_POINT_STATE_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_DISH_POINT_STATE_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_DISH_POINT_STATE_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_DISH_POINT_ATTR, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_POINT_ATTR + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_DISH_POINT_ATTR, int(tango.LogLevel.LOG_ERROR))

    def dishCapturingCallback(self, evt):
        """
        Retrieves the subscribed capturing attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on capturing attribute.

        :return: None

        """
        if evt.err is False:
            try:
                self._dish_capturing = evt.attr_value.value
                if self._dish_capturing is True:
                    print(CONST.STR_DISH_CAPTURING_TRUE)
                    self._read_activity_message = CONST.STR_DISH_CAPTURING_TRUE
                elif self._dish_capturing is False:
                    print(CONST.STR_DISH_CAPTURING_FALSE)
                    self._read_activity_message = CONST.STR_DISH_CAPTURING_FALSE
                else:
                    print(CONST.STR_DISH_CAPTURING_UNKNOWN, evt)
                    self._read_activity_message = CONST.STR_DISH_CAPTURING_UNKNOWN + str(evt)
            except Exception as except_occurred:
                print(CONST.ERR_DISH_CAPTURING_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_DISH_CAPTURING_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_DISH_CAPTURING_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_SUBSR_CAPTURING_ATTR, evt.errors)
            self._read_activity_message = CONST.ERR_SUBSR_CAPTURING_ATTR + str(evt.errors)
            self.dev_logging(CONST.ERR_SUBSR_CAPTURING_ATTR, int(tango.LogLevel.LOG_ERROR))

    def dishAchievedPointingCallback(self, evt):
        """
        Retrieves the subscribed achievedPointing attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on achievedPointing attribute.

        :return: None

        """
        if evt.err is False:
            try:
                self._achieved_pointing = evt.attr_value.value
                print(CONST.STR_ACHIEVED_POINTING, self._achieved_pointing)
                self._read_activity_message = CONST.STR_ACHIEVED_POINTING + str(self._achieved_pointing)
            except Exception as except_occurred:
                print(CONST.ERR_DISH_ACHVD_POINT, except_occurred.message)
                self._read_activity_message = CONST.ERR_DISH_ACHVD_POINT + str(except_occurred.message)
                self.dev_logging(CONST.ERR_DISH_ACHVD_POINT, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_DISH_ACHVD_ATTR, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_ACHVD_ATTR + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_DISH_ACHVD_ATTR, int(tango.LogLevel.LOG_ERROR))

    def dishDesiredPointingCallback(self, evt):
        """
        Retrieves the subscribed desiredPointing attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on desiredPointing attribute.

        :return: None

        """
        if evt.err is False:
            try:
                self._desired_pointing = evt.attr_value.value
                print(CONST.STR_DESIRED_POINTING, self._desired_pointing)
                self._read_activity_message = CONST.STR_DESIRED_POINTING + str(self._desired_pointing)
            except Exception as except_occurred:
                print(CONST.ERR_DISH_DESIRED_POINT, except_occurred.message)
                self._read_activity_message = CONST.ERR_DISH_DESIRED_POINT + str(except_occurred.message)
                self.dev_logging(CONST.ERR_DISH_DESIRED_POINT, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR, int(tango.LogLevel.LOG_ERROR))

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on DishMaster.

        :param event: response from DishMaster for the invoked command

        :return: None

        """
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                #print(CONST.ERR_INVOKING_CMD + event.cmd_name + "\n" + str(event.errors))
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                self.dev_logging(log, int(tango.LogLevel.LOG_ERROR))
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.dev_logging(log, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occurred:
            #print(CONST.ERR_EXCEPT_CMD_CB, except_occurred)
            self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            self.dev_logging(CONST.ERR_EXCEPT_CMD_CB, int(tango.LogLevel.LOG_ERROR))


    def dmstodd(self, dish_antenna_latitude):
        """Converts latitude from deg:min:sec to decimal degree format.

        :param dish_antenna_latitude: latitude of Dish location in Deg:Min:Sec.

        :return: latitude of Dish location in decimal Degree.

        """
        dd = re.split('[:]+', dish_antenna_latitude)
        deg_dec = abs(float(dd[0])) + ((float(dd[1])) / 60) + ((float(dd[2])) / 3600)
        if "-" in dd[0]:
            return deg_dec * (-1)
        else:
            return deg_dec

    def convert_radec_to_azel(self, data):
        """Converts RaDec coordinate in to AzEl coordinate using KATPoint library.

        :param data: DevVarStringArray
        Argin to be provided is the Ra and Dec values in the following format: radec|2:31:50.91|89:15:51.4
        Where first value is tag that is radec, second value is Ra in Hr:Min:Sec,and third value is Dec in
        Deg:Min:Sec.

        :return: None.

        """
        try:
            # Setting Observer Position as Pune
            dish_antenna = katpoint.Antenna(name= self.dish_name ,
                                            latitude=self.observer_location_lat,
                                            longitude=self.observer_location_long,
                                            altitude=self.observer_altitude)
            # Antenna latitude
            dish_antenna_latitude = dish_antenna.ref_observer.lat

            # Compute Target Coordinates
            target_radec = data[0]
            desired_target = katpoint.Target(target_radec)
            timestamp = katpoint.Timestamp(timestamp=data[1])
            target_apparnt_radec = katpoint.Target.apparent_radec(desired_target,
                                                                  timestamp=timestamp,
                                                                  antenna=dish_antenna)

            # TODO: Conversion of apparent ra and dec using katpoint library for future refererence.
            #target_apparnt_ra = katpoint._ephem_extra.angle_from_hours(target_apparnt_radec[0])
            #target_apparnt_dec = katpoint._ephem_extra.angle_from_degrees(target_apparnt_radec[1])

            # calculate sidereal time in radians
            side_time = dish_antenna.local_sidereal_time(timestamp=timestamp)
            side_time_radian = katpoint.deg2rad(math.degrees(side_time))

            # converting ra to ha
            hour_angle = side_time_radian - target_apparnt_radec[0]
            # TODO: Conversion of hour angle from radian to HH:MM:SS for future refererence.
            #print("Hour angle in hours: ", katpoint._ephem_extra.angle_from_hours(hour_angle))

            # Geodetic latitude of the observer
            # TODO: For refererence
            #latitude_degree_decimal = float(18) + float(31) / 60 + float(48) / (60 * 60)
            latitude_degree_decimal = self.dmstodd(str(dish_antenna_latitude))
            latitude_radian = katpoint.deg2rad(latitude_degree_decimal)

            # Calculate enu coordinates
            enu_array = katpoint.hadec_to_enu(hour_angle, target_apparnt_radec[1], latitude_radian)

            # Calculate Az El coordinates
            self.az_el_coordinates = katpoint.enu_to_azel(enu_array[0], enu_array[1], enu_array[2])
            self.az = katpoint.rad2deg(self.az_el_coordinates[0])
            self.el = katpoint.rad2deg(self.az_el_coordinates[1])
            self.RaDec_AzEl_Conversion = True

        except ValueError:
            print(CONST.ERR_RADEC_TO_AZEL_VAL_ERR)
            self.RaDec_AzEl_Conversion = False
            self._read_activity_message = CONST.ERR_RADEC_TO_AZEL_VAL_ERR
            self.dev_logging(CONST.ERR_RADEC_TO_AZEL_VAL_ERR, int(tango.LogLevel.LOG_ERROR))

        except Exception as except_occurred:
            self.RaDec_AzEl_Conversion = False
            self._read_activity_message = CONST.ERR_RADEC_TO_AZEL + str(except_occurred)
            self.dev_logging(CONST.ERR_RADEC_TO_AZEL, int(tango.LogLevel.LOG_ERROR))

    def tracking_time_thread(self):
        """This thread allows the dish to track the source for a specified Duration.

        :return: None.

        """
        start_track_time = time.time()
        end_track_time = start_track_time + self.TrackDuration * 60.0
        while 1:
            if end_track_time <= time.time():
                self.event_track_time.set()
                self._read_activity_message = CONST.ERR_TIME_LIM
                print(CONST.ERR_TIME_LIM)
                break
            elif self.el_limit == True:
                break

    def track_thread(self, argin):
        """This thread invokes Track command on DishMaster at the rate of 20 Hz.

        :param argin: DevVarStringArray

        For Track thread, argin to be provided is the Ra and Dec values in the following format:
        radec|2:31:50.91|89:15:51.4 Where first value is tag that is radec, second value is Ra in Hr:Min:Sec,
        and third value is Dec in Deg:Min:Sec.

        It takes system's current time in UTC as timestamp and converts RaDec to AzEl using
        convert_radec_to_azel method of class DishLeafNode.

        :return: None.

        """
        radec_value = argin.replace('|', ',')
        # RaDec as input argument

        #Timestamp value if given as input argument
        #timestamp_value = argin[1].replace('|', ' ')

        try:
            while self.event_track_time.is_set() is False:
                # timestamp_value = Current system time in UTC
                timestamp_value = str(datetime.datetime.utcnow())
                katpoint_arg = []
                katpoint_arg.insert(0, radec_value)
                katpoint_arg.insert(1, timestamp_value)
                # Conversion of RaDec to AzEl
                self.convert_radec_to_azel(katpoint_arg)
                if self.RaDec_AzEl_Conversion is True:
                    if self.el >= 17.5 and self.el <= 90:
                        if self.az < 0:
                            self.az = 360 - abs(self.az)

                        roundoff_az_el = [round(self.az, 12), round(self.el, 12)]
                        spectrum = [0]
                        spectrum.extend((roundoff_az_el))
                        # assign calculated AzEl to desiredPointing attribute of Dishmaster
                        self._dish_proxy.desiredPointing = spectrum
                        # Invoke Track command of Dish Master
                        self._dish_proxy.command_inout_asynch(CONST.CMD_TRACK, "0", self.commandCallback)
                    else:
                        self.el_limit = True
                        self._read_activity_message = CONST.ERR_ELE_LIM
                        break
                else:
                    break
                time.sleep(0.05)
        except Exception as except_occurred:
            print(CONST.ERR_EXE_TRACK, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_TRACK + str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_TRACK, int(tango.LogLevel.LOG_ERROR))

# PROTECTED REGION END #    //  DishLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------
    DishMasterFQDN = device_property(
        dtype='str',
        doc="FQDN of Dish Master Device",
    )

    TrackDuration = device_property(
        dtype='int', default_value=0.5
    )

    # ----------
    # Attributes
    # ----------
    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    dishHealthState = attribute(name="dishHealthState", label="dishHealthState", forwarded=True)

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """
        Initializes the attributes and properties of DishLeafNode and subscribes change event
        on attributes of DishMaster.

        :return: None

        """
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(DishLeafNode.init_device) ENABLED START #
        print(CONST.STR_INIT_LEAF_NODE)
        self._read_activity_message = CONST.STR_INIT_LEAF_NODE
        self.SkaLevel = 3
        self.el = 50.0
        self.az = 0
        self.RaDec_AzEl_Conversion = False
        self.ele_max_lim = 90
        self.horizon_el = 0
        self.ele_min_lim = 17.5
        self.dish_name = 'd1'
        self.observer_location_lat = '18:31:48:00'
        self.observer_location_long = '73:50:23.99'
        self.observer_altitude = 570
        self.el_limit = False
        try:
            print(CONST.STR_DISHMASTER_FQN, self.DishMasterFQDN)
            self._read_activity_message = CONST.STR_DISHMASTER_FQN + str(self.DishMasterFQDN)
            self._dish_proxy = DeviceProxy(self.DishMasterFQDN)   #Creating proxy to the DishMaster

            #
            #self.event_el = threading.Event()
            self.event_track_time = threading.Event()
        except Exception as except_occurred:
            print(CONST.ERR_IN_CREATE_PROXY_DM, except_occurred)
            self._read_activity_message = CONST.ERR_IN_CREATE_PROXY_DM + str(except_occurred)
            self.set_state(DevState.FAULT)
        self._admin_mode = 0                                    #Setting adminMode to "ONLINE"
        self._health_state = 0                                  #Setting healthState to "OK"
        self._simulation_mode = False                           #Enabling the simulation mode
        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        print(CONST.STR_SETTING_CB_MODEL, ApiUtil.instance().get_asynch_cb_sub_model())
        self._read_activity_message = CONST.STR_SETTING_CB_MODEL + str(
            ApiUtil.instance().get_asynch_cb_sub_model())
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
            self.dev_logging(CONST.STR_DISH_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occurred:
            print(CONST.ERR_SUBS_DISH_ATTR, except_occurred)
            self._read_activity_message = CONST.ERR_SUBS_DISH_ATTR + str(except_occurred)
            self.set_state(DevState.FAULT)
            self.set_status(CONST.ERR_DISH_INIT)
            self.dev_logging(CONST.ERR_DISH_INIT, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(DishLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  DishLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(DishLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  DishLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(DishLeafNode.activityMessage_read) ENABLED START #
        """ Returns the activityMessage """
        return self._read_activity_message
        # PROTECTED REGION END #    //  DishLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(DishLeafNode.activityMessage_write) ENABLED START #
        """ Sets the activityMessage """
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
        """ Triggers the DishMaster to transit into Stow Mode """
        self._dish_proxy.command_inout_asynch(CONST.CMD_SET_STOW_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  DishLeafNode.SetStowMode

    def is_SetStowMode_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_SetStowMode_allowed) ENABLED START #
        return self._dish_proxy.state() not in [DevState.ON, DevState.ALARM]
        # PROTECTED REGION END #    //  DishLeafNode.is_SetStowMode_allowed

    @command(
    )
    @DebugIt()
    def SetStandByLPMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStandByLPMode) ENABLED START #
        """ Triggers the DishMaster to transit into STANDBY-LP mode (i.e. Low Power State) """
        self._dish_proxy.command_inout_asynch(CONST.CMD_SET_STANDBYLP_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  DishLeafNode.SetStandByLPMode

    def is_SetStandByLPMode_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_SetStandbyLPMode_allowed) ENABLED START #
        print(self._dish_proxy.pointingState)
        print(self._dish_proxy.pointingState not in [1, 2, 3])
        return self._dish_proxy.pointingState not in [1, 2, 3]
        # PROTECTED REGION END #    //  DishLeafNode.is_SetStandbyLPMode_allowed

    @command(
    )
    @DebugIt()
    def SetOperateMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetOperateMode) ENABLED START #
        """ Triggers the DishMaster to transit into Operate mode. """
        self._dish_proxy.command_inout_asynch(CONST.CMD_SET_OPERATE_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  DishLeafNode.SetOperateMode

    def is_SetOperateMode_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_SetOperateMode_allowed) ENABLED START #
        return self._dish_proxy.state() not in [DevState.ON, DevState.ALARM, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishLeafNode.is_SetOperateMode_allowed

    @command(
        dtype_in='str',
        doc_in="Timestamp",
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Scan) ENABLED START #
        """
        Triggers the DishMaster to start the Scan.

        :param argin: timestamp

        :return: None

        """
        try:
            if type(float(argin)) == float:
                print(CONST.STR_IN_SCAN)
                self._dish_proxy.command_inout_asynch(CONST.CMD_DISH_SCAN,
                                                      argin, self.commandCallback)
                print(CONST.STR_OUT_SCAN)
        except Exception as except_occurred:
            print(CONST.ERR_EXE_SCAN_CMD, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_SCAN_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.Scan

    @command(
        dtype_in='str',
        doc_in="Timestamp",
    )
    @DebugIt()
    def EndScan(self, argin):
        # PROTECTED REGION ID(DishLeafNode.EndScan) ENABLED START #
        """ Triggers the DishMaster to stop the Scan.

        :param argin: timestamp

        :return: None

        """
        try:
            if type(float(argin)) == float:
                self._dish_proxy.command_inout_asynch(CONST.CMD_STOP_CAPTURE,
                                                      argin, self.commandCallback)
        except Exception as except_occurred:
            print(CONST.ERR_EXE_END_SCAN_CMD, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_END_SCAN_CMD+ str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_END_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.EndScan

    @command(
        dtype_in=('str',),
        doc_in="Pointing parameter of Dish",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Configure) ENABLED START #
        """
        Configures the Dish by setting pointing coordinates for a given observation.

        :param argin: String array that includes pointing parameters of Dish - Azimuth and Elevation Angle.

        :return: None

        """
        try:
            # Convert ra and dec to az and el
            radec_value = argin[0].replace('|', ',')
            timestamp_value = argin[1].replace('|', ' ')
            katpoint_arg = []
            katpoint_arg.insert(0, radec_value)
            katpoint_arg.insert(1, timestamp_value)
            self.convert_radec_to_azel(katpoint_arg)

            # Invoke slew command on DishMaster with az and el as inputs
            if self.el >= self.horizon_el  and self.el < self.ele_max_lim:
                # To obtain positive value of azimuth coordinate
                if self.az < 0:
                    self.az = 360 - abs(self.az)
                roundoff_az_el = [round(self.az, 2), round(self.el, 2)]
                spectrum = [0]
                spectrum.extend((roundoff_az_el))
                self._dish_proxy.desiredPointing = spectrum
                self._dish_proxy.command_inout_asynch(CONST.CMD_DISH_SLEW, "0", self.commandCallback)
            else:
                self._read_activity_message = CONST.STR_TARGET_NOT_OBSERVED
        except Exception as except_occurred:
            print(CONST.ERR_EXE_CONFIGURE_CMD, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_CONFIGURE_CMD +  str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_CONFIGURE_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.Configure

    def is_Configure_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_Configure_allowed) ENABLED START #
        """ Checks if the Configure command is allowed in the current state of DishLeafNode """
        return self.get_state() not in [DevState.INIT, DevState.DISABLE, DevState.OFF]
        # PROTECTED REGION END #    //  DishLeafNode.is_Configure_allowed

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
    )
    @DebugIt()
    def StartCapture(self, argin):
        # PROTECTED REGION ID(DishLeafNode.StartCapture) ENABLED START #
        """ Triggers the DishMaster to Start capture on the set configured band.

        :param argin: timestamp

        :return: None

        """
        try:
            if type(float(argin)) == float:
                self._dish_proxy.command_inout_asynch(CONST.CMD_START_CAPTURE,
                                                      argin, self.commandCallback)
        except Exception as except_occurred:
            print(CONST.ERR_EXE_START_CAPTURE_CMD, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_START_CAPTURE_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_START_CAPTURE_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.StartCapture

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
    )
    @DebugIt()
    def StopCapture(self, argin):
        # PROTECTED REGION ID(DishLeafNode.StopCapture) ENABLED START #
        """
        Triggers the DishMaster to Stop capture on the set configured band.

        :param argin: timestamp

        :return: None

        """
        try:
            if type(float(argin)) == float:
                self._dish_proxy.command_inout_asynch(CONST.CMD_STOP_CAPTURE, argin, self.commandCallback)
        except Exception as except_occurred:
            print(CONST.ERR_EXE_STOP_CAPTURE_CMD, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_STOP_CAPTURE_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_STOP_CAPTURE_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.StopCapture

    @command(
    )
    @DebugIt()
    def SetStandbyFPMode(self):
        # PROTECTED REGION ID(DishLeafNode.SetStandbyFPMode) ENABLED START #
        """ Triggers the DishMaster to transition into the STANDBY-FP (Standby-Full power) mode. """
        self._dish_proxy.command_inout_asynch(CONST.CMD_SET_STANDBYFP_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  DishLeafNode.SetStandbyFPMode

    def is_SetStandbyFPMode_allowed(self):
        # PROTECTED REGION ID(DishLeafNode.is_SetStandbyFPMode_allowed) ENABLED START #
        return self._dish_proxy.state() not in [DevState.UNKNOWN, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishLeafNode.is_SetStandbyFPMode_allowed

    @command(
        dtype_in='str',
        doc_in="Timestamp at which command should be executed.",
    )
    @DebugIt()
    def Slew(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Slew) ENABLED START #
        """
        Triggers the DishMaster to slew the dish towards the set pointing coordinates.

        :param argin: timestamp

        :return: None

        """
        try:
            if type(float(argin)) == float:
                self._dish_proxy.command_inout_asynch(CONST.CMD_DISH_SLEW, argin, self.commandCallback)
        except Exception as except_occurred:
            print(CONST.ERR_EXE_SLEW_CMD, except_occurred)
            self._read_activity_message = CONST.ERR_EXE_SLEW_CMD + str(except_occurred)
            self.dev_logging(CONST.ERR_EXE_SLEW_CMD, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  DishLeafNode.Slew

    @command(
        dtype_in=('str',),
    )
    @DebugIt()
    def Track(self, argin):
        # PROTECTED REGION ID(DishLeafNode.Track) ENABLED START #
        """ Invokes Track command on the DishMaster.

        :param argin: DevVarStringArray

        The elevation limit thread allows Dish to track a source till the observation capacity i.e.
        elevation limit of dish.

        The tracking time thread allows dish to track a source for the prespecified Track Duration
        (provided elevation limit is not reached).

        For Track command, Argin to be provided is the Ra and Dec values in the following format:
        radec|2:31:50.91|89:15:51.4 Where first value is tag that is radec, second value is Ra in Hr:Min:Sec,
        and third value is Dec in Deg:Min:Sec.

        :return: None

        """
        self.el_limit = False
        self.event_track_time.clear()
        self.tracking_time_thread1 = threading.Thread(None, self.tracking_time_thread, CONST.THREAD_TRACK)
        self.tracking_time_thread1.start()
        self.track_thread1 = threading.Thread(None, self.track_thread, CONST.THREAD_TRACK, args=argin)
        self.track_thread1.start()
        # PROTECTED REGION END #    //  DishLeafNode.Track

# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(DishLeafNode.main) ENABLED START #
    """
    Runs the DishLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: DishLeafNode TANGO object.
    """
    return run((DishLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  DishLeafNode.main

if __name__ == '__main__':
    main()
