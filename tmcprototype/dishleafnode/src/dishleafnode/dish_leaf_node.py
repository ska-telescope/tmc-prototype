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

import json
import importlib.resources

# PROTECTED REGION ID(DishLeafNode.additionnal_import) ENABLED START #
# PyTango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute
from ska.base.commands import ResultCode, ResponseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, SimulationMode

# Additional import
# PROTECTED REGION ID(DishLeafNode.additionnal_import) ENABLED START #
import threading
from . import const
import math
import katpoint
import re
import datetime
import time
# PROTECTED REGION END #    //  DishLeafNode.additionnal_import

__all__ = ["DishLeafNode", "main"]

class DishLeafNode(SKABaseDevice):
#class DishLeafNode(SKABaseDevice):
    """
    A Leaf control node for DishMaster.
    """

    # PROTECTED REGION ID(DishLeafNode.class_variable) ENABLED START #
    def dish_mode_cb(self, evt):
        """
        Retrieves the subscribed dishMode attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on dishMode attribute.

        :return: None

        """
        try:
            log_msg = "DishMode Event is: " + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._dish_mode = evt.attr_value.value
                if self._dish_mode == 0:
                    self.logger.debug(const.STR_DISH_OFF_MODE)
                    self._read_activity_message = const.STR_DISH_OFF_MODE
                elif self._dish_mode == 1:
                    self.logger.debug(const.STR_DISH_STARTUP_MODE)
                    self._read_activity_message = const.STR_DISH_STARTUP_MODE
                elif self._dish_mode == 2:
                    self.logger.debug(const.STR_DISH_SHUTDOWN_MODE)
                    self._read_activity_message = const.STR_DISH_SHUTDOWN_MODE
                elif self._dish_mode == 3:
                    self.logger.debug(const.ERR_DISH_MODE_CB)
                    self._read_activity_message = const.STR_DISH_STANDBYLP_MODE
                elif self._dish_mode == 4:
                    self.logger.debug(const.STR_DISH_STANDBYFP_MODE)
                    self._read_activity_message = const.STR_DISH_STANDBYFP_MODE
                elif self._dish_mode == 5:
                    self.logger.debug(const.STR_DISH_MAINT_MODE)
                    self._read_activity_message = const.STR_DISH_MAINT_MODE
                elif self._dish_mode == 6:
                    self.logger.debug(const.STR_DISH_STOW_MODE)
                    self._read_activity_message = const.STR_DISH_STOW_MODE
                elif self._dish_mode == 7:
                    self.logger.debug(const.STR_DISH_CONFIG_MODE)
                    self._read_activity_message = const.STR_DISH_CONFIG_MODE
                elif self._dish_mode == 8:
                    self.logger.debug(const.STR_DISH_OPERATE_MODE)
                    self._read_activity_message = const.STR_DISH_OPERATE_MODE
                else:
                    log_msg = const.STR_DISH_UNKNOWN_MODE + str(evt)
                    self.logger.debug(log_msg)
                    self._read_activity_message = const.STR_DISH_UNKNOWN_MODE + str(evt)
            else:
                log_msg = const.ERR_ON_SUBS_DISH_MODE_ATTR + str(evt.errors)
                self.logger.debug(log_msg)
                self._read_activity_message = const.ERR_ON_SUBS_DISH_MODE_ATTR + str(evt.errors)
                self.logger.error(const.ERR_ON_SUBS_DISH_MODE_ATTR)
        except Exception as except_occurred:
            log_msg = const.ERR_DISH_MODE_CB + str(except_occurred.message)
            self.logger.error(log_msg)
            self._handle_generic_exception(except_occurred, [], 0, const.ERR_DISH_MODE_CB)


    def dish_capturing_cb(self, evt):
        """
        Retrieves the subscribed capturing attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on capturing attribute.

        :return: None

        """
        try:
            log_msg = "Capturing attribute Event is: " + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._dish_capturing = evt.attr_value.value
                if self._dish_capturing is True:
                    self.logger.debug(const.STR_DISH_CAPTURING_TRUE)
                    self._read_activity_message = const.STR_DISH_CAPTURING_TRUE
                elif self._dish_capturing is False:
                    self.logger.debug(const.STR_DISH_CAPTURING_FALSE)
                    self._read_activity_message = const.STR_DISH_CAPTURING_FALSE
                else:
                    log_msg = const.STR_DISH_CAPTURING_UNKNOWN + str(evt)
                    self.logger.debug(log_msg)
                    self._read_activity_message = const.STR_DISH_CAPTURING_UNKNOWN + str(evt)
            else:
                log_msg = const.ERR_SUBSR_CAPTURING_ATTR + str(evt.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_SUBSR_CAPTURING_ATTR + str(evt.errors)
                self.logger.error(const.ERR_SUBSR_CAPTURING_ATTR)
        except Exception as except_occurred:
            log_msg = const.ERR_DISH_CAPTURING_CB + str(except_occurred.message)
            self.logger.error(log_msg)
            self._handle_generic_exception(except_occurred, [], 0, const.ERR_DISH_CAPTURING_CB)

    def dish_achieved_pointing_cb(self, evt):
        """
        Retrieves the subscribed achievedPointing attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on achievedPointing attribute.

        :return: None

        """
        try:
            log_msg = "AchievedPointing attribute Event is: " + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._achieved_pointing = evt.attr_value.value
                log_msg = const.STR_ACHIEVED_POINTING + str(self._achieved_pointing)
                self.logger.debug(log_msg)
                self._read_activity_message = const.STR_ACHIEVED_POINTING + str(self._achieved_pointing)
            else:
                log_msg = const.ERR_ON_SUBS_DISH_ACHVD_ATTR + str(evt.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_ON_SUBS_DISH_ACHVD_ATTR + str(evt.errors)
                self.logger.error(const.ERR_ON_SUBS_DISH_ACHVD_ATTR)
        except Exception as except_occurred:
            log_msg = const.ERR_DISH_ACHVD_POINT + str(except_occurred.message)
            self.logger.error(log_msg)
            self._handle_generic_exception(except_occurred, [], 0, const.ERR_DISH_ACHVD_POINT)


    def dish_desired_pointing_cb(self, evt):
        """
        Retrieves the subscribed desiredPointing attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on desiredPointing attribute.

        :return: None

        """
        try:
            log_msg = "DesiredPointing attribute Event is: " + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                self._desired_pointing = evt.attr_value.value
                log_msg = const.STR_DESIRED_POINTING + str(self._desired_pointing)
                self.logger.error(log_msg)
                self._read_activity_message = const.STR_DESIRED_POINTING + str(self._desired_pointing)
            else:
                log_msg = const.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR + str(evt.errors)
                self.logger.error(log_msg)
                self._read_activity_message = const.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR + str(evt.errors)
                self.logger.error(const.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR)
        except Exception as except_occurred:
            log_msg = const.ERR_DISH_DESIRED_POINT + str(except_occurred.message)
            self.logger.error(log_msg)
            self._handle_generic_exception(except_occurred, [], 0, const.ERR_DISH_DESIRED_POINT)


    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on DishMaster.

        :param event: a CmdDoneEvent object. This class is used to pass data
            to the callback method in asynchronous callback model for command
            execution.
        :type: CmdDoneEvent object
            It has the following members:
                - device     : (DeviceProxy) The DeviceProxy object on which the
                               call was executed.
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to true if the command
                               failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext
        :return: none

        """
        exception_count = 0
        exception_message = []
        # Update logs and activity message attribute with received event
        try:
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                self._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                self._read_activity_message = log_msg

        except Exception as except_occurred:
            [exception_count,exception_message] = self._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, const.ERR_EXCEPT_CMD_CB)

        # Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_CMD_CALLBK)

    def dmstodd(self, dish_antenna_latitude):
        """Converts latitude from deg:min:sec to decimal degree format.

        :param dish_antenna_latitude: latitude of Dish location in Deg:Min:Sec.
        Example: 18:31:48.0

        :return: latitude of Dish location in decimal Degree.
        Example : "18.529999999999998" is the returned value of dmstodd
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
        Argin to be provided is the Ra and Dec values in the following format:
        radec|21:08:47.92|89:15:51.4
        Where first value is tag that is radec, second value is Ra in Hr:Min:Sec,and third value is Dec in
        Deg:Min:Sec.

        :return: None.

        """
        try:
            # Create Antenna Object
            dish_antenna = katpoint.Antenna(name= self.dish_name ,
                                            latitude=self.observer_location_lat,
                                            longitude=self.observer_location_long,
                                            altitude=self.observer_altitude)
            # Antenna latitude
            dish_antenna_latitude = dish_antenna.ref_observer.lat

            # Compute Target Coordinates
            target_radec = data[0]
            desired_target = katpoint.Target(str(target_radec))
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
        except ValueError as value_err:
            self.logger.error(const.ERR_RADEC_TO_AZEL_VAL_ERR)
            self.RaDec_AzEl_Conversion = False
            self._read_activity_message = const.ERR_RADEC_TO_AZEL_VAL_ERR + str(value_err)
            self.logger.error(const.ERR_RADEC_TO_AZEL_VAL_ERR)
        except Exception as except_occurred:
            self.RaDec_AzEl_Conversion = False
            self._handle_generic_exception(except_occurred, [], 0, const.ERR_RADEC_TO_AZEL)

    def tracking_time_thread(self):
        """This thread allows the dish to track the source for a specified Duration.

        :return: None.

        """
        start_track_time = time.time()
        end_track_time = start_track_time + self.TrackDuration * 60.0
        while 1:
            if end_track_time <= time.time():
                self.event_track_time.set()
                self._read_activity_message = const.ERR_TIME_LIM
                self.logger.error(const.ERR_TIME_LIM)
                break
            elif self.el_limit == True:
                break

    def track_thread(self, argin):
        """This thread invokes Track command on DishMaster at the rate of 20 Hz.

        :param argin: DevVarStringArray

        For Track thread, argin to be provided is the Ra and Dec values in the following format:
        radec|21:08:47.92|89:15:51.4 Where first value is tag that is radec, second value is Ra in Hr:Min:Sec,
        and third value is Dec in Deg:Min:Sec.

        It takes system's current time in UTC as timestamp and converts RaDec to AzEl using
        convert_radec_to_azel method of class DishLeafNode.

        :return: None.

        """

        try:
            while self.event_track_time.is_set() is False:
                # timestamp_value = Current system time in UTC
                timestamp_value = str(datetime.datetime.utcnow())
                katpoint_arg = []
                katpoint_arg.insert(0, argin)
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
                        self._dish_proxy.command_inout_asynch(const.CMD_TRACK, "0", self.cmd_ended_cb)
                    else:
                        self.el_limit = True
                        self._read_activity_message = const.ERR_ELE_LIM
                        break
                else:
                    break
                time.sleep(0.05)
                # self._dish_proxy.pointingState = 0
        except Exception as except_occurred:
            self.logger.error(const.ERR_EXE_TRACK, str(except_occurred))
            self.logger.error(const.ERR_EXE_TRACK)
            self._handle_generic_exception(except_occurred, [], 0, const.ERR_EXE_TRACK)

    # Function for handling all Devfailed exception
    def _handle_devfailed_exception(self, df, except_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(df)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(df)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    def _handle_generic_exception(self, exception, except_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(exception)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(exception)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    def throw_exception(self, except_msg_list, read_actvity_msg):
        err_msg = ''
        for item in except_msg_list:
            err_msg += item + "\n"
        tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)

    def dms_to_rad(self,dms):
        deg = float(dms[0])
        min = float(dms[1])
        sec = float(dms[2])
        rad_value = ((math.pi / 180) * ((deg) + (min / 60) + (sec / 3600)))
        return rad_value

    def rad_to_dms(self, rad_value):
        dms = []
        frac_min , deg = math.modf(rad_value * (180 / math.pi))
        frac_sec, min = math.modf(frac_min * 60)
        sec = frac_sec * 60
        dms.append(deg)
        dms.append(min)
        dms.append(sec)
        return dms

    def set_dish_name_number(self):
        # Find out dish number from DishMasterFQDN property
        dish_name_string = self.DishMasterFQDN.split("/")
        dish_num_list = [ dish_name_char for dish_name_char in dish_name_string[0] if dish_name_char.isdigit()]
        self.dish_number = "".join(dish_num_list)
        self.dish_name = 'd' + self.dish_number

    def set_observer_lat_long_alt(self):
        # Load a set of antenna descriptions (latitude, longitude, altitude, enu coordinates) from text file and
        # construct Antenna objects from them. Currently the text file contains Meerkat Antenna parameters.
        with importlib.resources.open_text("dishleafnode", "ska_antennas.txt") as f:
            descriptions = f.readlines()
        antennas = [katpoint.Antenna(line) for line in descriptions]
        for ant in antennas:
            if ant.name == self.dish_number:
                ref_ant_lat = ant.ref_observer.lat
                ref_ant_long = ant.ref_observer.long
                ref_ant_altitude = ant.ref_observer.elevation
                ant_delay_model = ant.delay_model.values()
        # Convert reference antenna lat and long into radian
        ref_ant_lat_rad = self.dms_to_rad(str(ref_ant_lat).split(":"))
        ref_ant_long_rad = self.dms_to_rad(str(ref_ant_long).split(":"))

        # Find latitude, longitude and altitude of Dish antenna
        # Convert enu to ecef coordinates for dish
        dish_ecef_coordinates = katpoint.enu_to_ecef(ref_ant_lat_rad, ref_ant_long_rad, ref_ant_altitude,
                                                       ant_delay_model[0], ant_delay_model[1], ant_delay_model[2])
        # Convert ecef to lla coordinates for dish (in radians)
        dish_lat_long_alt_rad = katpoint.ecef_to_lla(dish_ecef_coordinates[0], dish_ecef_coordinates[1],
                                                       dish_ecef_coordinates[2])
        # Convert lla coordinates from rad to dms
        dish_lat_dms = self.rad_to_dms(dish_lat_long_alt_rad[0])
        dish_long_dms = self.rad_to_dms(dish_lat_long_alt_rad[1])

        self.observer_location_lat = str(dish_lat_dms[0]) + ":" + str(dish_lat_dms[1]) + ":" + str(dish_lat_dms[2])
        self.observer_location_long = str(dish_long_dms[0]) + ":" + str(dish_long_dms[1]) + ":" + str(dish_long_dms[2])
        self.observer_altitude = dish_ecef_coordinates[2]

# PROTECTED REGION END #    //  DishLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------
    DishMasterFQDN = device_property(
        dtype='str',default_value="mid_d0001/elt/master",
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
    dishPointingState = attribute(name="dishPointingState",label="dishPointingState",forwarded=True
    )
    # ---------------
    # General methods
    # ---------------


    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC DishLeafNode's init_device() "command".
        """
        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()
            device = self.target

            self.logger.info(const.STR_INIT_LEAF_NODE)
            device.SkaLevel = 3
            device.el = 50.0
            device.az = 0
            device.RaDec_AzEl_Conversion = False
            device.ele_max_lim = 90
            device.horizon_el = 0
            device.ele_min_lim = 17.5
            device.el_limit = False
            _state_fault_flag = False  # flag use to check whether state set to fault if exception occurs.
            exception_message = []
            exception_count = 0
            try:
                device.set_dish_name_number()
                device.set_observer_lat_long_alt()
                log_msg = const.STR_DISHMASTER_FQDN + str(device.DishMasterFQDN)
                self.logger.debug(log_msg)
                device._read_activity_message = log_msg
                device._dish_proxy = DeviceProxy(str(device.DishMasterFQDN))   #Creating proxy to the DishMaster
                device.event_track_time = threading.Event()
            except DevFailed as dev_failed:
                _state_fault_flag = True
                device._handle_devfailed_exception(dev_failed,exception_message, exception_count,const.ERR_IN_CREATE_PROXY_DM)
            device._health_state = HealthState.OK                                    #Setting healthState to "OK"
            device._simulation_mode = SimulationMode.FALSE                           #Enabling the simulation mode
            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            self.logger.error(log_msg)
            device._read_activity_message = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            # Subscribing to DishMaster Attributes
            try:
                device._dish_proxy.subscribe_event(const.EVT_DISH_MODE, EventType.CHANGE_EVENT,
                                                 device.dish_mode_cb, stateless=True)
                device._dish_proxy.subscribe_event(const.EVT_DISH_CAPTURING, EventType.CHANGE_EVENT,
                                                 device.dish_capturing_cb, stateless=True)
                device._dish_proxy.subscribe_event(const.EVT_ACHVD_POINT, EventType.CHANGE_EVENT,
                                                 device.dish_achieved_pointing_cb, stateless=True)
                device._dish_proxy.subscribe_event(const.EVT_DESIRED_POINT, EventType.CHANGE_EVENT,
                                                 device.dish_desired_pointing_cb, stateless=True)
                device.set_status(const.STR_DISH_INIT_SUCCESS)
                self.logger.info(const.STR_DISH_INIT_SUCCESS)
            except DevFailed as dev_failed:
                device._handle_devfailed_exception(dev_failed,exception_message, exception_count,
                                                 const.ERR_SUBS_DISH_ATTR)
                device.set_status(const.ERR_DISH_INIT)
                _state_fault_flag = True
                self.logger.error(const.ERR_DISH_INIT)

            if _state_fault_flag:
                message = const.ERR_DISH_INIT
                return_code = ResultCode.FAILED
            else:
                message = const.STR_DISH_INIT_SUCCESS
                return_code = ResultCode.OK

            device._read_activity_message = message
            self.logger.info(message)
            return (return_code, message)


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
        """ Internal construct of TANGO. Sets the activityMessage """
        self._read_activity_message = value
        # PROTECTED REGION END #    //  DishLeafNode.activityMessage_write

    # --------
    # Commands
    # --------

    class SetStowModeCommand(ResponseCommand):
        """
        A class for DishLeafNode's SetStowMode command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            device = self.target
            if device._dish_proxy.state() in [DevState.ON, DevState.ALARM]:
                tango.Except.throw_exception("Command SetStowMode is not allowed in current state.",
                                             "Failed to invoke SetStowMode command on DishMaster.",
                                             "DishLeafNode.SetStowMode()",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self):
            """ Triggers the DishMaster to transit into Stow Mode. """
            device = self.target
            device._dish_proxy.command_inout_asynch(const.CMD_SET_STOW_MODE, device.cmd_ended_cb)
            return (ResultCode.STARTED, const.STR_SET_STOW_MODE_SUCCESS)

    def is_SetStowMode_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("SetStowMode")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def SetStowMode(self):
        """ Triggers the DishMaster to transit into Stow Mode. """
        handler = self.get_command_object("SetStowMode")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class SetStandByLPModeCommand(ResponseCommand):
        """
        A class for DishLeafNode's SetStandByLPMode command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            device = self.target
            if device._dish_proxy.pointingState in [1, 2, 3]:
                tango.Except.throw_exception("SetStandByLPMode() is not allowed in current state",
                                             "Failed to invoke SetStandByLpMode command on DishMaster.",
                                             "DishLeafNode.SetStandByLPMode() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self):
            """ Triggers the DishMaster to transit into STANDBY-LP mode (i.e. Low Power State). """
            device = self.target
            device._dish_proxy.command_inout_asynch(const.CMD_SET_STANDBYLP_MODE, device.cmd_ended_cb)
            return (ResultCode.OK, const.STR_SETSTANDBYLP_SUCCESS)

    def is_SetStandByLPMode_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("SetStandByLPMode")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def SetStandByLPMode(self):
        """ Triggers the DishMaster into STANDBY-LP mode (i.e. Low Power State). """
        handler = self.get_command_object("SetStandByLPMode")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class SetOperateModeCommand(ResponseCommand):
        """
        A class for DishLeafNode's SetOperateMode command.
        """
        def check_allowed(self):

            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            device = self.target
            if device._dish_proxy.state() in [DevState.ON, DevState.ALARM, DevState.DISABLE]:
                tango.Except.throw_exception("SetOperateMode() is not allowed in current state",
                                             "Failed to invoke SetOperateMode command on DishMaster.",
                                             "DishLeafNode.SetOperateMode() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self):
            """ Triggers the DishMaster to transit into Operate mode. """
            device = self.target
            device._dish_proxy.command_inout_asynch(const.CMD_SET_OPERATE_MODE, device.cmd_ended_cb)
            return (ResultCode.OK, const.STR_SETOPERATE_SUCCESS)

    def is_SetOperateMode_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("SetOperateMode")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def SetOperateMode(self):
        """ Triggers the DishMaster to transit into Operate mode. """
        handler = self.get_command_object("SetOperateMode")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class ScanCommand(ResponseCommand):
        """
        A class for DishLeafNode's Scan() command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Scan() is not allowed in current state",
                                             "Failed to invoke Scan command on DishLeafNode.",
                                             "DishLeafNode.Scan() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """
            Triggers the DishMaster to start the Scan.

            :param argin: timestamp

            :return: None

            TODO: Scan argument in JSON format
            {"scanDuration": 10.0}

            """

            device = self.target
            exception_count = 0
            exception_message = []
            # TODO: Accept Scan argument in JSON format
            # jsonArgument = json.loads(argin)
            # scan_duration = jsonArgument['scanDuration']
            # print("Scan duration:", scan_duration)
            try:
                if type(float(argin)) == float:
                    self.logger.debug(const.STR_IN_SCAN)
                    device._dish_proxy.command_inout_asynch(const.CMD_DISH_SCAN,
                                                          argin, device.cmd_ended_cb)
                    self.logger.debug(const.STR_OUT_SCAN)
                    return (ResultCode.OK, const.STR_SCAN_SUCCESS)
            except ValueError as value_error:
                log_msg = const.ERR_EXE_SCAN_CMD + const.ERR_INVALID_DATATYPE + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_EXE_SCAN_CMD + const.ERR_INVALID_DATATYPE + \
                                              str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1


            # Throw Exception
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_SCAN_EXEC)
                return (ResultCode.FAILED, const.ERR_EXE_SCAN_CMD)

    def is_Scan_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("Scan")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="Timestamp",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Scan(self, argin):
        """ Triggers the DishMaster to start the Scan. """
        handler = self.get_command_object("Scan")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class EndScanCommand(ResponseCommand):
        """
        A class for DishLeafNode's EndScan() command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("EndScan() is not allowed in current state",
                                             "Failed to invoke StopCapture command on DishLeafNode.",
                                             "DishLeafNode.EndScan() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """
            Triggers the DishMaster to stop the Scan.

            :param argin: timestamp

            :return: None
            TODO: EndScan argument in JSON format
            {"timestamp": 0}
            """

            device = self.target
            exception_count = 0
            exception_message = []
            # TODO: Accept EndScan argument in JSON format
            # jsonArgument = json.loads(argin)
            # timestamp = jsonArgument['timestamp']
            # print("End Scan timestamp:", timestamp)
            try:
                if type(float(argin)) == float:
                    device._dish_proxy.command_inout_asynch(const.CMD_STOP_CAPTURE,
                                                          argin, device.cmd_ended_cb)
                    return (ResultCode.OK, const.STR_ENDSCAN_SUCCESS)
            except ValueError as value_error:
                log_msg = const.ERR_EXE_END_SCAN_CMD + const.ERR_INVALID_DATATYPE + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_EXE_END_SCAN_CMD + const.ERR_INVALID_DATATYPE + \
                                              str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            # Throw Exception
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_ENDSCAN_EXEC)
                return (ResultCode.FAILED, const.ERR_EXE_END_SCAN_CMD)

    def is_EndScan_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="Timestamp",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def EndScan(self, argin):
        """ Triggers the DishMaster to stop the Scan. """
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class ConfigureCommand(ResponseCommand):
        """
        A class for DishLeafNode's Configure() command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE, DevState.INIT]:
                tango.Except.throw_exception("Configure() is not allowed in current state",
                                             "Failed to invoke Configure command on DishLeafNode.",
                                             "DishLeafNode.Configure() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """
            Configures the Dish by setting pointing coordinates for a given observation.
            This function accepts the input json and calculate pointing parameters of Dish- Azimuth
            and Elevation Angle.Calculated parameters again converted to json and fed to the dish master.

            :param argin:
            A String in a JSON format that includes pointing parameters of Dish- Azimuth and Elevation Angle.

                Example:
                {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
                "dish":{"receiverBand":"1"}}

            :return: None

            """

            device = self.target
            exception_count = 0
            exception_message = []
            try:
                jsonArgument = json.loads(argin)
                ra_value = (jsonArgument["pointing"]["target"]["RA"])
                dec_value = (jsonArgument["pointing"]["target"]["dec"])
                receiver_band = int(jsonArgument["dish"]["receiverBand"])
                # timestamp_value = Current system time in UTC
                timestamp_value = str(datetime.datetime.utcnow())
                # Convert ra and dec to az and el
                radec_value = 'radec' + ',' + str(ra_value) + ',' + str(dec_value)
                katpoint_arg = []
                katpoint_arg.insert(0, radec_value)
                katpoint_arg.insert(1, timestamp_value)
                device.convert_radec_to_azel(katpoint_arg)
                # Convert calulated AZ-El into JSON string
                arg_list = {"pointing": {
                    "AZ": device.az,
                    "EL": device.el

                },
                    "dish": {
                        "receiverBand": receiver_band
                    }

                }
                dish_str_ip = json.dumps(arg_list)
                # Send configure command to Dish Master
                device._dish_proxy.command_inout_asynch(const.CMD_DISH_CONFIGURE, str(dish_str_ip),
                                                      device.cmd_ended_cb)
                return (ResultCode.OK, const.STR_CONFIGURE_SUCCESS)

            except ValueError as value_error:
                device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
                log_msg = const.ERR_INVALID_JSON + str(value_error)
                self.logger.error(log_msg)
                exception_message.append(const.ERR_INVALID_JSON + str(value_error))
                exception_count += 1

            except KeyError as key_error:
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                self.logger.error(log_msg)
                exception_message.append(const.ERR_JSON_KEY_NOT_FOUND + str(key_error))
                exception_count += 1

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                    exception_message, exception_count, const.ERR_EXE_CONFIGURE_CMD)

            except Exception as except_occurred:
                log_msg = const.ERR_EXE_CONFIGURE_CMD + str(except_occurred)
                self.logger.error(log_msg)
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                    exception_message, exception_count, const.ERR_EXE_CONFIGURE_CMD)

            # Throw Exception
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_CONFIGURE_EXEC)
                return (ResultCode.FAILED, str(exception_message))

    def is_Configure_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="Pointing parameter of Dish",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Configure(self, argin):
        """ Configures the Dish by setting pointing coordinates for a given observation. """
        handler = self.get_command_object("Configure")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]


    class StartCaptureCommand(ResponseCommand):
        """
        A class for DishLeafNode's StartCapture command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,]:
                tango.Except.throw_exception("StartCapture() is not allowed in current state",
                                             "Failed to invoke StartCapture command on DishLeafNode.",
                                             "DishLeafNode.StartCapture() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """ Triggers the DishMaster to Start capture on the set configured band.

                :param argin: timestamp

                :return: None

            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                if type(float(argin)) == float:
                    device._dish_proxy.command_inout_asynch(const.CMD_START_CAPTURE,
                                                          argin, device.cmd_ended_cb)
                    return (ResultCode.OK, const.STR_STARTCAPTURE_SUCCESS)
            except ValueError as value_error:
                log_msg = const.ERR_EXE_START_CAPTURE_CMD + const.ERR_INVALID_DATATYPE + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_EXE_START_CAPTURE_CMD + const.ERR_INVALID_DATATYPE + \
                                              str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            # Throw Exception
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_STARTCAPTURE_EXEC)
                # TODO: Test case is failing due to following statement
                return (ResultCode.FAILED, const.ERR_EXE_START_CAPTURE_CMD)

    def is_StartCapture_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("StartCapture")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StartCapture(self, argin):
        """ Triggers the DishMaster to Start capture on the set configured band. """
        handler = self.get_command_object("StartCapture")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class StopCaptureCommand(ResponseCommand):
        """
        A class for DishLeafNode's StopCapture command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("StopCapture() is not allowed in current state",
                                             "Failed to invoke StopCapture command on DishLeafNode.",
                                             "DishLeafNode.StopCapture() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """
            Triggers the DishMaster to Stop capture on the set configured band.

            :param argin: timestamp

            :return: None
            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                if type(float(argin)) == float:
                    device._dish_proxy.command_inout_asynch(const.CMD_STOP_CAPTURE, argin, device.cmd_ended_cb)
                    return (ResultCode.OK, const.STR_STOPCAPTURE_SUCCESS)
            except ValueError as value_error:
                log_msg = const.ERR_EXE_STOP_CAPTURE_CMD + const.ERR_INVALID_DATATYPE + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_EXE_STOP_CAPTURE_CMD + const.ERR_INVALID_DATATYPE + \
                                              str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            # Throw Exception
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_STOPCAPTURE_EXEC)
                return (ResultCode.FAILED, const.ERR_EXE_STOP_CAPTURE_CMD)

    def is_StopCapture_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("StopCapture")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StopCapture(self, argin):
        """ Triggers the DishMaster to Stop capture on the set configured band. """
        handler = self.get_command_object("StopCapture")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class SetStandbyFPModeCommand(ResponseCommand):
        """
        A class for DishLeafNode's SetStandByFPMode command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            device = self.target
            if device._dish_proxy.state() in [DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("SetStandbyFPMode() is not allowed in current state",
                                             "Failed to invoke SetStandbyFPMode command on DishMaster.",
                                             "DishLeafNode.SetStandbyFPMode() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self):
            """ Triggers the DishMaster to transition into the STANDBY-FP (Standby-Full power) mode. """
            device = self.target
            device._dish_proxy.command_inout_asynch(const.CMD_SET_STANDBYFP_MODE, device.cmd_ended_cb)
            return (ResultCode.OK, const.STR_STANDBYFP_SUCCESS)

    def is_SetStandbyFPMode_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("SetStandbyFPMode")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def SetStandbyFPMode(self):
        """ Triggers the DishMaster to transition into the STANDBY-FP (Standby-Full power) mode. """
        handler = self.get_command_object("SetStandbyFPMode")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class SlewCommand(ResponseCommand):
        """
        A class for DishLeafNode's SlewCommand command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Slew() is not allowed in current state",
                                             "Failed to invoke Slew command on DishLeafNode.",
                                             "DishLeafNode.Slew() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """
            Triggers the DishMaster to slew the dish towards the set pointing coordinates.

            :param argin: timestamp

            :return: None
            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                if type(float(argin)) == float:
                    device._dish_proxy.command_inout_asynch(const.CMD_DISH_SLEW, argin, device.cmd_ended_cb)
                    return (ResultCode.OK, const.STR_SLEW_SUCCESS)
            except ValueError as value_error:
                log_msg = const.ERR_EXE_SLEW_CMD + const.ERR_INVALID_DATATYPE + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_EXE_SLEW_CMD + "\n" + const.ERR_INVALID_DATATYPE + \
                                              str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            # Throw Exception
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_SLEW_EXEC)
                return (ResultCode.FAILED, const.ERR_EXE_SLEW_CMD)

    def is_Slew_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("Slew")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="Timestamp at which command should be executed.",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Slew(self, argin):
        """ Triggers the DishMaster to slew the dish towards the set pointing coordinates. """
        handler = self.get_command_object("Slew")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class TrackCommand(ResponseCommand):
        """
        A class for DishLeafNode's Track command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Track() is not allowed in current state",
                                             "Failed to invoke Track command on DishLeafNode.",
                                             "DishLeafNode.Track() ",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self, argin):
            """ Invokes Track command on the DishMaster.

            :param argin: DevString

            The elevation limit thread allows Dish to track a source till the observation capacity i.e.
            elevation limit of dish.

            The tracking time thread allows dish to track a source for the prespecified Track Duration
            (provided elevation limit is not reached).

            For Track command, Argin to be provided is the Ra and Dec values in the following JSON format:

            {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
            "dish":{"receiverBand":"1"}}

            :return: None

            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                device.el_limit = False
                jsonArgument = json.loads(argin)
                ra_value = (jsonArgument["pointing"]["target"]["RA"])
                dec_value = (jsonArgument["pointing"]["target"]["dec"])
                radec_value = 'radec' + ',' + str(ra_value) + ',' + str(dec_value)
                device.event_track_time.clear()
                # TODO: For future reference
                # self.tracking_time_thread1 = threading.Thread(None, self.tracking_time_thread, const.THREAD_TRACK)
                # self.tracking_time_thread1.start()
                # Pass string argument in track_thread in brackets
                device.track_thread1 = threading.Thread(None, device.track_thread, const.THREAD_TRACK,
                                                      args=(radec_value,))
                device.track_thread1.start()
                return (ResultCode.OK, const.STR_TRACK_SUCCESS)

            except ValueError as value_error:
                device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
                log_msg = const.ERR_INVALID_JSON + str(value_error)
                self.logger.error(log_msg)
                exception_message.append(const.ERR_INVALID_JSON + str(value_error))
                exception_count += 1

            except KeyError as key_error:
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                device.logger.error(log_msg)
                exception_message.append(const.ERR_JSON_KEY_NOT_FOUND + str(key_error))
                exception_count += 1

            # Throw Exception
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_TRACK_EXEC)
                return (ResultCode.FAILED, str(exception_message))

    def is_Track_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("Track")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Track(self, argin):
        """ Invokes Track command on the DishMaster. """
        handler = self.get_command_object("Track")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class StopTrackCommand(ResponseCommand):
        """
        A class for DishLeafNode's StopTrack command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("StopTrack() is not allowed in current state",
                                             "Failed to invoke StopTrack command on DishLeafNode.",
                                             "DishLeafNode.StopTrack() ",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self):
            """
                Invokes StopTrack command on the DishMaster.

                :param argin: DevVoid

                :return: None

            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                device.event_track_time.set()
                device._dish_proxy.command_inout_asynch(const.CMD_STOP_TRACK, device.cmd_ended_cb)
                return (ResultCode.OK, const.STR_STOP_TRACK_SUCCESS)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                        exception_message,
                                                                                        exception_count,
                                                                                        const.ERR_EXE_STOP_TRACK_CMD)

            except Exception as except_occurred:
                log_msg = const.ERR_EXE_STOP_TRACK_CMD + str(except_occurred.message)
                self.logger.info(log_msg)
                [exception_count, exception_message] = device._handle_generic_exception(except_occurred,
                                                                                      exception_message,
                                                                                      exception_count,
                                                                                      const.ERR_EXE_STOP_TRACK_CMD)

            # Throw Exception
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_STOPTRACK_EXEC)
                return (ResultCode.FAILED, const.ERR_EXE_STOP_TRACK_CMD)

    def is_StopTrack_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
            current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
            in current device state
        """
        handler = self.get_command_object("StopTrack")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StopTrack(self):
        """ Invokes StopTrack command on the DishMaster."""
        handler = self.get_command_object("StopTrack")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("SetStowMode", self.SetStowModeCommand(*args))
        self.register_command_object("SetStandByLPMode", self.SetStandByLPModeCommand(*args))
        self.register_command_object("SetOperateMode", self.SetOperateModeCommand(*args))
        self.register_command_object("Scan", self.ScanCommand(*args))
        self.register_command_object("EndScan", self.EndScanCommand(*args))
        self.register_command_object("Configure", self.ConfigureCommand(*args))
        self.register_command_object("StartCapture", self.StartCaptureCommand(*args))
        self.register_command_object("StopCapture", self.StopCaptureCommand(*args))
        self.register_command_object("SetStandbyFPMode", self.SetStandbyFPModeCommand(*args))
        self.register_command_object("Slew", self.SlewCommand(*args))
        self.register_command_object("Track", self.TrackCommand(*args))
        self.register_command_object("StopTrack", self.StopTrackCommand(*args))

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
