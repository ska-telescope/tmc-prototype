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
import json
import importlib.resources
import math
import datetime
import time
import threading

import tango
from tango import DeviceProxy, EventType, ApiUtil, DevState, AttrWriteType, DevFailed, DebugIt
from tango.server import run, command, device_property, attribute
import katpoint

from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, SimulationMode
from .utils import PointingState, UnitConverter
from . import const, release

__all__ = ["DishLeafNode", "main"]


class CommandCallBack:
    def __init__(self, device, log):
        self.device = device
        self.logger = log

    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on DishMaster.

        :param event: a CmdDoneEvent object. This object is used to pass data
            to the callback method in asynchronous callback model for command
            execution.
        :type: CmdDoneEvent object
                It has the following members:
                - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext
        :return: none

        """
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            self.device._read_activity_message = log_msg
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            self.device._read_activity_message = log_msg


# pylint: disable=unused-variable, logging-fstring-interpolation
class DishLeafNode(SKABaseDevice):
    """
    A Leaf control node for DishMaster.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd_ended_cb = CommandCallBack(self, self.logger).cmd_ended_cb

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("SetStowMode", self.SetStowModeCommand(*args))
        self.register_command_object("SetStandbyLPMode", self.SetStandbyLPModeCommand(*args))
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
        self.register_command_object("Abort", self.AbortCommand(*args))
        self.register_command_object("Restart", self.RestartCommand(*args))
        self.register_command_object("ObsReset", self.ObsResetCommand(*args))

    @staticmethod
    def _throw_exception(command_name, log_message):
        tango.Except.throw_exception(
            "{} command execution".format(command_name),
            log_message,
            "DishLeafNode.{}Command".format(command_name),
            tango.ErrSeverity.ERR,
        )

    def attribute_event_handler(self, event_data):
        """
        Retrieves the subscribed attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on attribute.

        :return: None
        """
        if event_data.err:
            log_msg = f"Event system DevError(s) occured!!! {str(event_data.errors)}"
            self._read_activity_message = log_msg
            self.logger.error(log_msg)
            return

        fqdn_attr_name = event_data.attr_name
        # tango://monctl.devk4.camlab.kat.ac.za:4000/mid_dish_0000/elt/
        # master/<attribute_name>#dbase=no
        # We process the FQDN of the attribute to extract just the
        # attribute name. Also handle the issue with the attribute name being
        # converted to lowercase in subsequent callbacks.
        attr_name = fqdn_attr_name.split("/")[-1].split("#")[0]
        log_msg = f"{attr_name} is {event_data.attr_value.value}."
        self._read_activity_message = log_msg
        self.logger.debug(log_msg)

    def convert_radec_to_azel(self, data):
        """Converts RaDec coordinate in to AzEl coordinate using KATPoint library.

        :param data: DevVarStringArray
        Argin to be provided is the Ra and Dec values in the following format:
        radec|21:08:47.92|89:15:51.4
        Where first value is tag that is radec, second value is Ra in Hr:Min:Sec,and third value is Dec in
        Deg:Min:Sec.

        :return: None.

        :raises: Exception if error occurs in Ra-Dec to Az-El conversion

        """
        dish_antenna = katpoint.Antenna(
            name=self.dish_name,
            latitude=self.observer_location_lat,
            longitude=self.observer_location_long,
            altitude=self.observer_altitude,
        )

        dish_antenna_latitude = dish_antenna.ref_observer.lat

        # Compute Target Coordinates
        target_radec = data[0]
        desired_target = katpoint.Target(str(target_radec))
        timestamp = katpoint.Timestamp(timestamp=data[1])

        try:
            target_apparnt_radec = katpoint.Target.apparent_radec(
                desired_target, timestamp=timestamp, antenna=dish_antenna
            )
        except ValueError as value_err:
            raise value_err

        sidereal_time = dish_antenna.local_sidereal_time(timestamp=timestamp)
        sidereal_time_radian = katpoint.deg2rad(math.degrees(sidereal_time))

        # converting ra to ha
        hour_angle = sidereal_time_radian - target_apparnt_radec[0]

        # Geodetic latitude of the observer
        latitude_degree_decimal = UnitConverter().dms_to_dd(str(dish_antenna_latitude))
        latitude_radian = katpoint.deg2rad(latitude_degree_decimal)

        # Calculate enu coordinates
        enu_array = katpoint.hadec_to_enu(hour_angle, target_apparnt_radec[1], latitude_radian)

        # Calculate Az El coordinates
        az_el_coordinates = katpoint.enu_to_azel(enu_array[0], enu_array[1], enu_array[2])
        return az_el_coordinates

    def tracking_time_thread(self):
        """This thread allows the dish to track the source for a specified Duration.

        :return: None.

        """
        start_track_time = time.time()
        end_track_time = start_track_time + self.TrackDuration * 60.0
        while True:
            if end_track_time <= time.time():
                self.event_track_time.set()
                self._read_activity_message = const.ERR_TIME_LIM
                self.logger.error(const.ERR_TIME_LIM)
                break
            elif self.el_limit:
                break

    def track_thread(self):
        """This thread invokes Track command on DishMaster at the rate of 20 Hz.

        :return: None.
        """
        self.logger.info(
            f"print track_thread thread name:{threading.currentThread().getName()}"
            f"{threading.get_ident()}"
        )
        while self.event_track_time.is_set() is False:
            timestamp_value = str(datetime.datetime.utcnow())
            katpoint_arg = [self.radec_value, timestamp_value]

            try:
                az_el_coordinates = self.convert_radec_to_azel(katpoint_arg)
            except ValueError as valuerr:
                log_msg = f"Exception occured in the execution of Track command. {valuerr}"
                self.logger.error(log_msg)
                self._read_activity_message = log_msg
                return
            
            self.az = katpoint.rad2deg(az_el_coordinates[0])
            self.el = katpoint.rad2deg(az_el_coordinates[1])

            if not self._is_elevation_within_mechanical_limits():
                time.sleep(0.05)
                continue

            if self.az < 0:
                self.az = 360 - abs(self.az)

            desired_pointing = [0, round(self.az, 12), round(self.el, 12)]
            self._dish_proxy.desiredPointing = desired_pointing
            if self.event_track_time.is_set():
                log_msg = f"Exiting thread loop. Event track time set: {self.event_track_time.is_set()}"
                self.logger.debug(log_msg)
                break

            time.sleep(0.05)

    def _is_elevation_within_mechanical_limits(self):
        if not (self.el >= self.ele_min_lim and self.el <= self.ele_max_lim):
            self.el_limit = True
            self._read_activity_message = const.ERR_ELE_LIM
            self.logger.info(const.ERR_ELE_LIM)
            self._read_activity_message = const.STR_SRC_NOT_VISIBLE
            self.logger.info(const.STR_SRC_NOT_VISIBLE)
            return False
        return True
            
    def set_dish_name_number(self):
        # Find out dish number from DishMasterFQDN property e.g. mid_d0001/elt/master
        dish_name_string = self.DishMasterFQDN.split("/")[0]
        self.dish_name = dish_name_string.split("_")[1]
        self.dish_number = self.dish_name[1:]

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
        obj_unitconverter = UnitConverter()
        ref_ant_lat_rad = obj_unitconverter.dms_to_rad(str(ref_ant_lat).split(":"))
        ref_ant_long_rad = obj_unitconverter.dms_to_rad(str(ref_ant_long).split(":"))

        # Find latitude, longitude and altitude of Dish antenna
        # Convert enu to ecef coordinates for dish
        dish_ecef_coordinates = katpoint.enu_to_ecef(
            ref_ant_lat_rad,
            ref_ant_long_rad,
            ref_ant_altitude,
            ant_delay_model[0],
            ant_delay_model[1],
            ant_delay_model[2],
        )
        # Convert ecef to lla coordinates for dish (in radians)
        dish_lat_long_alt_rad = katpoint.ecef_to_lla(
            dish_ecef_coordinates[0], dish_ecef_coordinates[1], dish_ecef_coordinates[2]
        )
        # Convert lla coordinates from rad to dms
        dish_lat_dms = obj_unitconverter.rad_to_dms(dish_lat_long_alt_rad[0])
        dish_long_dms = obj_unitconverter.rad_to_dms(dish_lat_long_alt_rad[1])

        self.observer_location_lat = f"{dish_lat_dms[0]}:{dish_lat_dms[1]}:{dish_lat_dms[2]}"
        self.observer_location_long = f"{dish_long_dms[0]}:{dish_long_dms[1]}:{dish_long_dms[2]}"
        self.observer_altitude = dish_ecef_coordinates[2]

    # -----------------
    # Device Properties
    # -----------------
    DishMasterFQDN = device_property(
        dtype="str",
        default_value="mid_d0001/elt/master",
        doc="FQDN of Dish Master Device",
    )

    TrackDuration = device_property(dtype="int", default_value=0.5)

    # ----------
    # Attributes
    # ----------
    activityMessage = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    def read_activityMessage(self):
        """ Returns the activityMessage """
        return self._read_activity_message

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage """
        self._read_activity_message = value

    dishHealthState = attribute(name="dishHealthState", label="dishHealthState", forwarded=True)

    dishPointingState = attribute(
        name="dishPointingState", label="dishPointingState", forwarded=True
    )

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC DishLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the DishLeafNode.

            :return: A tuple containing a return code and a string message indicating status. The message is for
                information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs in creating proxy for DishMaster or in subscribing the event on DishMaster
            """
            # TODO: The code is implemented such way that even in case of exception,
            #  the execution will continue. It is possible that due to this,
            #  the device may get incorrectly initialised. Its better to exit on first
            #  occurrence of an exception.

            super().do()
            device = self.target

            self.logger.info("Initializing DishLeafNode...")
            device.el = 30.0
            device.az = 0.0
            device.ele_max_lim = 90
            device.ele_min_lim = 17.5
            device.el_limit = False
            device._build_state = f"{release.name},{release.version},{release.description}"
            device._version_id = release.version
            device.radec_value = ""
            device.set_dish_name_number()
            device.set_observer_lat_long_alt()
            log_message = f"DishMasterFQDN :-> {device.DishMasterFQDN}"
            self.logger.debug(log_message)
            device._read_activity_message = log_message
            device.event_track_time = threading.Event()
            device._health_state = HealthState.OK
            device._simulation_mode = SimulationMode.FALSE

            try:
                device._dish_proxy = DeviceProxy(str(device.DishMasterFQDN))
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_message = "Error in creating proxy to the Dish Master"
                device._read_activity_message = log_message
                self._throw_exception("Init", log_message)

            attributes_to_subscribe_to = (
                "dishMode",
                "capturing",
                "achievedPointing",
                "desiredPointing",
            )

            self._subscribe_to_attribute_events(attributes_to_subscribe_to)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_message = (
                f"{const.STR_SETTING_CB_MODEL}{ApiUtil.instance().get_asynch_cb_sub_model()}"
            )
            self.logger.debug(log_message)
            device._read_activity_message = log_message
            log_message = "Dish Leaf Node initialized successfully."
            device.set_status(log_message)
            device._read_activity_message = log_message
            self.logger.info(log_message)
            return (ResultCode.OK, device._read_activity_message)

        def _subscribe_to_attribute_events(self, attributes):
            device = self.target
            for attribute_name in attributes:
                try:
                    device._dish_proxy.subscribe_event(
                        attribute_name,
                        EventType.CHANGE_EVENT,
                        device.attribute_event_handler,
                        stateless=True,
                    )
                except DevFailed as dev_failed:
                    self.logger.exception(dev_failed)
                    log_msg = (
                        f"Exception occurred while subscribing to Dish attribute: {attribute_name}"
                    )
                    device.set_status(const.ERR_DISH_INIT)
                    device._read_activity_message = log_msg


    class SetStowModeCommand(BaseCommand):
        """
        A class for DishLeafNode's SetStowMode() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state.

            """
            return True

        def do(self):
            """
            Invokes SetStowMode command on DishMaster.

            :return: None

            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("SetStowMode", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception in SetStowMode command"
                device._read_activity_message = log_msg
                self._throw_exception("SetStowMode", log_msg)

    def is_SetStowMode_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("SetStowMode")
        return handler.check_allowed()

    @command()
    def SetStowMode(self):
        """ Invokes SetStowMode command on DishMaster. """
        handler = self.get_command_object("SetStowMode")
        handler()

    class SetStandbyLPModeCommand(BaseCommand):
        """
        A class for DishLeafNode's SetStandbyLPMode() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state.

            """
            device = self.target
            if device._dish_proxy.pointingState in [
                PointingState.SLEW,
                PointingState.TRACK,
                PointingState.SCAN,
            ]:
                return False
            return True

        def do(self):
            """
            Invokes SetStandbyLPMode (i.e. Low Power State) command on DishMaster.

            :return: None

            """
            device = self.target

            try:
                device._dish_proxy.command_inout_asynch("SetStandbyLPMode", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                log_msg = "Exception in SetStandbyLPMode command"
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                self._throw_exception("SetStandbyLPMode", log_msg)

    def is_SetStandbyLPMode_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("SetStandbyLPMode")
        return handler.check_allowed()

    @command()
    def SetStandbyLPMode(self):
        """ Invokes SetStandbyLPMode (i.e. Low Power State) command on DishMaster. """
        handler = self.get_command_object("SetStandbyLPMode")
        handler()

    class SetOperateModeCommand(BaseCommand):
        """
        A class for DishLeafNode's SetOperateMode() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean
            """
            return True

        def do(self):
            """
            Invokes SetOperateMode command on DishMaster.

            :return: None
            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("SetOperateMode", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception in SetOperateMode command"
                device._read_activity_message = log_msg
                self._throw_exception("SetOperateMode", log_msg)

    def is_SetOperateMode_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("SetOperateMode")
        return handler.check_allowed()

    @command()
    def SetOperateMode(self):
        """ Invokes SetOperateMode command on DishMaster. """
        handler = self.get_command_object("SetOperateMode")
        handler()

    class ScanCommand(BaseCommand):
        """
        A class for DishLeafNode's Scan() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean
            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                return False

            return True

        def do(self, argin):
            """
            Invokes Scan command on DishMaster.

            :param argin: timestamp

            :return: None

            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("Scan", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception in executing Scan command"
                device._read_activity_message = log_msg
                self._throw("Scan", log_msg)

    def is_Scan_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("Scan")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="Timestamp",
    )
    def Scan(self, argin):
        """ Invokes Scan command on DishMaster. """
        handler = self.get_command_object("Scan")
        handler(argin)

    class EndScanCommand(BaseCommand):
        """
        A class for DishLeafNode's EndScan() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                return False
            return True

        def do(self, argin):
            """
            Invokes EndScan command on DishMaster.

            :param argin: timestamp

            :return: None

            """

            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("StopCapture", device.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception in EndScan command"
                device._read_activity_message = log_msg
                self._throw_exception("EndScan", log_msg)

    def is_EndScan_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="Timestamp",
    )
    def EndScan(self, argin):
        """ Invokes StopCapture command on DishMaster. """
        handler = self.get_command_object("EndScan")
        handler(argin)

    class ConfigureCommand(BaseCommand):
        """
        A class for DishLeafNode's Configure() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state.

            """
            if self.state_model.op_state in [
                DevState.FAULT,
                DevState.UNKNOWN,
                DevState.DISABLE,
                DevState.INIT,
            ]:
                tango.Except.throw_exception(
                    "Configure() is not allowed in current state",
                    "Failed to invoke Configure command on DishLeafNode.",
                    "DishLeafNode.Configure() ",
                    tango.ErrSeverity.ERR,
                )

            return True

        def do(self, argin):
            """
            Configures the Dish by setting pointing coordinates for a given scan.
            This function accepts the input json and calculate pointing parameters of Dish- Azimuth
            and Elevation Angle. Calculated parameters are again converted to json and fed to the
            dish master.

            :param argin:
            A String in a JSON format that includes pointing parameters of Dish- Azimuth and Elevation Angle.

                Example:
                {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
                "dish":{"receiverBand":"1"}}

            :return: None

            :raises: DevFailed if error occurs while invoking this command on DishMaster.
                     ValueError if argin is not in valid JSON format.
                     KeyError if JSON key is not present in argin

            """

            device = self.target
            try:
                jsonArgument = json.loads(argin)
            except json.JSONDecodeError as jsonerr:
                log_msg = f"{const.ERR_INVALID_JSON}{jsonerr}"
                device._read_activity_message = log_msg
                self.logger.error(log_msg)
                tango.Except.throw_exception(
                    const.STR_CONFIGURE_EXEC,
                    log_msg,
                    "DishLeafNode.ConfigureCommand",
                    tango.ErrSeverity.ERR,
                )
            try:
                ra_value = jsonArgument["pointing"]["target"]["RA"]
                dec_value = jsonArgument["pointing"]["target"]["dec"]
                receiver_band = int(jsonArgument["dish"]["receiverBand"])
            except KeyError as key_error:
                log_msg = f"{const.ERR_JSON_KEY_NOT_FOUND}{key_error}"
                device._read_activity_message = log_msg
                self.logger.error(log_msg)
                tango.Except.throw_exception(
                    const.STR_CONFIGURE_EXEC,
                    log_msg,
                    "DishLeafNode.ConfigureCommand",
                    tango.ErrSeverity.ERR,
                )

            timestamp_value = str(datetime.datetime.utcnow())
            radec_value = f"radec,{ra_value},{dec_value}"
            katpoint_arg = []
            katpoint_arg.insert(0, radec_value)
            katpoint_arg.insert(1, timestamp_value)

            try:
                device.convert_radec_to_azel(katpoint_arg)
            except ValueError as valuerr:
                log_msg = f"{const.ERR_EXE_CONFIGURE_CMD}{valuerr}"
                device._read_activity_message = log_msg
                self.logger.error(log_msg)
                tango.Except.throw_exception(
                    const.STR_CONFIGURE_EXEC,
                    log_msg,
                    "DishLeafNode.ConfigureCommand",
                    tango.ErrSeverity.ERR,
                )

            arg_list = {
                "pointing": {"AZ": device.az, "EL": device.el},
                "dish": {"receiverBand": receiver_band},
            }
            dish_str_ip = json.dumps(arg_list)

            try:
                device._dish_proxy.command_inout_asynch(
                    const.CMD_DISH_CONFIGURE, str(dish_str_ip), self.cmd_ended_cb
                )
            except DevFailed as dev_failed:
                log_msg = f"{const.ERR_EXE_CONFIGURE_CMD}{dev_failed}"
                device._read_activity_message = log_msg
                self.logger.exception(log_msg)
                tango.Except.throw_exception(
                    const.STR_CONFIGURE_EXEC,
                    log_msg,
                    "DishLeafNode.ConfigureCommand",
                    tango.ErrSeverity.ERR,
                )

            device._read_activity_message = const.STR_CONFIGURE_SUCCESS
            self.logger.info(device._read_activity_message)

    def is_Configure_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="Pointing parameter of Dish",
    )
    def Configure(self, argin):
        """ Configures the Dish by setting pointing coordinates for a given observation. """
        handler = self.get_command_object("Configure")
        handler(argin)

    class StartCaptureCommand(BaseCommand):
        """
        A class for DishLeafNode's StartCapture() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            """
            if self.state_model.op_state in [
                DevState.FAULT,
                DevState.UNKNOWN,
                DevState.DISABLE,
            ]:
                return False

            return True

        def do(self, argin):
            """
            Invokes StartCapture command on DishMaster on the set configured band.

            :param argin: timestamp

            :return: None

            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("StartCapture", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception occurred in StartCapture command"
                device._read_activity_message = log_msg
                self._throw_exception("StartCapture", log_msg)

    def is_StartCapture_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("StartCapture")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
    )
    def StartCapture(self, argin):
        """ Triggers the DishMaster to Start capture on the set configured band. """
        handler = self.get_command_object("StartCapture")
        handler(argin)

    class StopCaptureCommand(BaseCommand):
        """
        A class for DishLeafNode's StopCapture() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state.

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception(
                    "StopCapture() is not allowed in current state",
                    "Failed to invoke StopCapture command on DishLeafNode.",
                    "DishLeafNode.StopCapture() ",
                    tango.ErrSeverity.ERR,
                )

            return True

        def do(self, argin):
            """
            Invokes StopCapture command on DishMaster on the set configured band.

            :param argin: timestamp

            :return: None

            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("StopCapture", device.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception occurred in StopCapture command"
                device._read_activity_message = log_msg
                self._throw_exception("StopCapture", log_msg)

    def is_StopCapture_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        handler = self.get_command_object("StopCapture")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start.",
    )
    def StopCapture(self, argin):
        """ Invokes StopCapture command on DishMaster on the set configured band. """
        handler = self.get_command_object("StopCapture")
        handler(argin)

    class SetStandbyFPModeCommand(BaseCommand):
        """
        A class for DishLeafNode's SetStandbyFPMode() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            """
            return True

        def do(self):
            """
            Invokes SetStandbyFPMode command on DishMaster (Standby-Full power) mode.

            :return:None

            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("SetStandbyFPMode", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                log_msg = "Exception in SetStandbyFPMode command"
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                self._throw_exception("SetStandbyFPMode", log_msg)

    def is_SetStandbyFPMode_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        """
        handler = self.get_command_object("SetStandbyFPMode")
        return handler.check_allowed()

    @command()
    def SetStandbyFPMode(self):
        """ Invokes SetStandbyFPMode command on DishMaster (Standby-Full power) mode. """
        handler = self.get_command_object("SetStandbyFPMode")
        handler()

    class SlewCommand(BaseCommand):
        """
        A class for DishLeafNode's SlewCommand() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state.

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception(
                    "Slew() is not allowed in current state",
                    "Failed to invoke Slew command on DishLeafNode.",
                    "DishLeafNode.Slew() ",
                    tango.ErrSeverity.ERR,
                )

            return True

        def do(self, argin):
            """
            Invokes Slew command on DishMaster to slew the dish towards the set pointing coordinates.

            :param argin: timestamp

            :return: None

            :raises: ValueError if argin is not in valid JSON format while invoking this
             command on DishMaster.

            """
            device = self.target

            try:
                float(argin)
            except ValueError as value_error:
                log_msg = f"{const.ERR_EXE_SLEW_CMD}{const.ERR_INVALID_DATATYPE}{value_error}"
                device._read_activity_message = log_msg
                self.logger.exception(value_error)
                tango.Except.throw_exception(
                    const.STR_STOPCAPTURE_EXEC,
                    log_msg,
                    "DishLeafNode.SlewCommand",
                    tango.ErrSeverity.ERR,
                )

            device._dish_proxy.command_inout_asynch("Slew", argin, self.cmd_ended_cb)
            device._read_activity_message = const.STR_SLEW_SUCCESS
            self.logger.info(device._read_activity_message)

    def is_Slew_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("Slew")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="Timestamp at which command should be executed.",
    )
    def Slew(self, argin):
        """ Invokes Slew command on DishMaster to slew the dish towards the set pointing coordinates. """
        handler = self.get_command_object("Slew")
        handler(argin)

    class TrackCommand(BaseCommand):
        """
        A class for DishLeafNode's Track() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                return False

            return True

        def do(self, argin):
            """Invokes Track command on the DishMaster.

            :param argin: DevString

            The elevation limit thread allows Dish to track a source till the observation capacity i.e.
            elevation limit of dish.

            The tracking time thread allows dish to track a source for the prespecified Track Duration
            (provided elevation limit is not reached).

            For Track command, argin to be provided is the Ra and Dec values in the following JSON format:

            {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
            "dish":{"receiverBand":"1"}}

            :return: None

            :raises: JSONDecodeError if argin is not a valid JSON format, KeyError if JSON key is
              not present in argin while invoking this command on DishMaster.

            """
            device = self.target
            device.el_limit = False

            jsonArgument = self._load_config_string(argin)
            ra_value, dec_value = self._get_targets(jsonArgument)
            device.radec_value = f"radec,{ra_value},{dec_value}"
            device.event_track_time.clear()

            try:
                device._dish_proxy.command_inout_asynch("Track", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.error(dev_failed)
                log_message = "Exception occured in the execution of Track command."
                self._read_activity_message = log_message
                self._throw_exception("Track", log_message)

            if device._dish_proxy.pointingState == PointingState.TRACK:
                device.tracking_thread = threading.Thread(None, device.track_thread, "DishLeafNode")
                if not device.tracking_thread.is_alive():
                    device.tracking_thread.start()

        def _get_targets(self, jsonArgument):
            device = self.target
            try:
                ra_value = jsonArgument["pointing"]["target"]["RA"]
                dec_value = jsonArgument["pointing"]["target"]["dec"]
            except KeyError as key_error:
                self.logger.exception(key_error)
                log_message = "JSON key not found."
                device._read_activity_message = log_message
                self._throw_exception("Track", log_message)

            return (ra_value, dec_value)

        def _load_config_string(self, argin):
            device = self.target
            try:
                jsonArgument = json.loads(argin)
            except json.JSONDecodeError as jsonerr:
                self.logger.exception(jsonerr)
                log_message = "Invalid JSON format."
                device._read_activity_message = log_message
                self._throw_exception("Track", log_message)

            return jsonArgument

    def is_Track_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("Track")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The JSON input string contains dish and pointing information.",
    )
    def Track(self, argin):
        """ Invokes Track command on the DishMaster. """
        handler = self.get_command_object("Track")
        handler(argin)

    class StopTrackCommand(BaseCommand):
        """
        A class for DishLeafNode's StopTrack() command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in the current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                return False
            return True

        def do(self):
            """
            Invokes StopTrack command on the DishMaster.

            :param argin: None.

            :return: None

            :raises: DevFailed if error occurs while invoking this command on DishMaster.

            """
            device = self.target
            device.event_track_time.set()
            try:
                device._dish_proxy.command_inout_asynch("TrackStop", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = "Exception occurred in StopTrack command"
                device._read_activity_message = log_msg
                self._throw_exception("StopTrack", log_msg)

    def is_StopTrack_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("StopTrack")
        return handler.check_allowed()

    @command()
    def StopTrack(self):
        """ Invokes StopTrack command on the DishMaster."""
        handler = self.get_command_object("StopTrack")
        handler()

    class AbortCommand(BaseCommand):
        """
        A class for DishLeafNode's Abort command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):

            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                return False
            return True

        def do(self):
            """
            Invokes Abort command on the DishMaster.

            :param argin: DevVoid

            :return: None

            :raises: DevFailed if error ocuurs while invoking command on DishMaster.
            """
            device = self.target
            device.event_track_time.set()
            try:
                device._dish_proxy.command_inout_asynch("TrackStop", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_msg = f"Exception occurred in Abort command"
                device._read_activity_message = log_msg
                self._throw_exception("Abort", log_msg)

    @command()
    def Abort(self):
        """ Invokes Abort command on the DishMaster."""
        handler = self.get_command_object("Abort")
        handler()

    def is_Abort_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean
        """
        handler = self.get_command_object("Abort")
        return handler.check_allowed()

    class RestartCommand(BaseCommand):
        """
        A class for DishLeafNode's Restart command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                return False
            return True

        def do(self):
            """
            Invokes Restart command on the DishMaster.

            :param argin: DevVoid

            :return: None

            raises: DevFailed if error occurs while invoking command on DishMaster
                    Exception if error occurs while executing the command

            """
            device = self.target
            try:
                device._dish_proxy.command_inout_asynch("SetStandbyLPMode", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                log_msg = "Exception occurred in Restart command"
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                self._throw_exception("Restart", log_msg)

    @command()
    def Restart(self):
        """ Invokes Restart command on the DishMaster."""
        handler = self.get_command_object("Restart")
        handler()

    def is_Restart_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean
        """
        handler = self.get_command_object("Restart")
        return handler.check_allowed()

    class ObsResetCommand(BaseCommand):
        """
        A class for DishLeafNode's ObsReset command.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cmd_ended_cb = CommandCallBack(self.target, self.logger).cmd_ended_cb

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
                return False
            return True

        def do(self):
            """
            Command to reset the Dishleaf Node and bring it to its RESETTING state.

            :param argin: None

            :return: None

            :raises: DevFailed if error occurs while invoking command on Dishleaf Node.
            """
            device = self.target

            try:
                device._dish_proxy.command_inout_asynch("SetStandbyFPMode", self.cmd_ended_cb)
            except DevFailed as dev_failed:
                log_msg = "Exception occurred in ObsReset command"
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                self._throw_exception("ObsReset", log_msg)

    @command()
    @DebugIt()
    def ObsReset(self):
        """ Invokes ObsReset command on the DishLeafNode."""
        handler = self.get_command_object("ObsReset")
        handler()

    def is_ObsReset_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        """
        handler = self.get_command_object("ObsReset")
        return handler.check_allowed()


# pylint: enable=unused-variable, logging-fstring-interpolation
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


if __name__ == "__main__":
    main()
