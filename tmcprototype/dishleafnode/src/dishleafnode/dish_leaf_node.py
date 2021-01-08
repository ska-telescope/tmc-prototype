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
import importlib.resources

import tango
from tango import ApiUtil, AttrWriteType
from tango.server import run, command, device_property, attribute
import katpoint

from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from tmc.common.tango_server_helper import TangoServerHelper
from ska.base.control_model import HealthState, SimulationMode
from .utils import UnitConverter
from . import release
from .device_data import DeviceData
from .abort_command import Abort
from .configure_command import Configure
from .endscan_command import EndScan
from .obsreset_command import ObsReset
from .restart_command import Restart
from .scan_command import Scan
from .setoperatemode_command import SetOperateMode
from .setstandbyfpmode_command import SetStandbyFPMode
from .setstandbylpmode_command import SetStandbyLPMode
from .setstowmode_command import SetStowMode
from .slew_command import Slew
from .startcapture_command import StartCapture
from .stopcapture_command import StopCapture
from .stoptrack_command import StopTrack
from .track_command import Track


__all__ = ["DishLeafNode", "main", "release", "SetOperateMode", "SetStandbyLPMode", "SetStandbyFPMode", "SetStowMode", "Scan", "EndScan", "StartCapture", "StopCapture",
                "Abort", "Restart", "ObsReset", "Slew", "Configure", "Track", "StopTrack"]


# class CommandCallBack:
#     def __init__(self, device, log):
#         self.device = device
#         self.logger = log

#     def cmd_ended_cb(self, event):
#         """
#         Callback function immediately executed when the asynchronous invoked
#         command returns. Checks whether the command has been successfully invoked on DishMaster.

#         :param event: a CmdDoneEvent object. This object is used to pass data
#             to the callback method in asynchronous callback model for command
#             execution.
#         :type: CmdDoneEvent object
#             It has the following members:
#             - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
#             - cmd_name   : (str) The command name
#             - argout_raw : (DeviceData) The command argout
#             - argout     : The command argout
#             - err        : (bool) A boolean flag set to True if the command failed.
#                             False otherwise
#             - errors     : (sequence<DevError>) The error stack
#             - ext
#         """
#         if event.err:
#             log_message = f"Error in invoking command: {event.cmd_name}\n{event.errors}"
#             self.logger.error(log_message)
#             self.device._read_activity_message = log_message
#         else:
#             log_message = f"Command :-> {event.cmd_name} invoked successfully."
#             self.logger.info(log_message)
#             self.device._read_activity_message = log_message


# pylint: disable=unused-variable, logging-fstring-interpolation
class DishLeafNode(SKABaseDevice):
    """
    A Leaf control node for DishMaster.
    """

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.cmd_ended_cb = CommandCallBack(self, self.logger).cmd_ended_cb

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        device_data = DeviceData.get_instance()

        args = (device_data, self.state_model, self.logger)

        self.register_command_object("SetStowMode", SetStowMode(*args))
        self.register_command_object("SetStandbyLPMode", SetStandbyLPMode(*args))
        self.register_command_object("SetOperateMode", SetOperateMode(*args))
        self.register_command_object("Scan", Scan(*args))
        self.register_command_object("EndScan", EndScan(*args))
        self.register_command_object("Configure", Configure(*args))
        self.register_command_object("StartCapture", StartCapture(*args))
        self.register_command_object("StopCapture", StopCapture(*args))
        self.register_command_object("SetStandbyFPMode", SetStandbyFPMode(*args))
        self.register_command_object("Slew", Slew(*args))
        self.register_command_object("Track", Track(*args))
        self.register_command_object("StopTrack", StopTrack(*args))
        self.register_command_object("Abort", Abort(*args))
        self.register_command_object("Restart", Restart(*args))
        self.register_command_object("ObsReset", ObsReset(*args))

    # def attribute_event_handler(self, event_data):
    #     """
    #     Retrieves the subscribed attribute of DishMaster.

    #     :param evt: A TANGO_CHANGE event on attribute.
    #     """
    #     if event_data.err:
    #         log_message = f"Event system DevError(s) occured!!! {str(event_data.errors)}"
    #         self._read_activity_message = log_message
    #         self.logger.error(log_message)
    #         return

    #     fqdn_attr_name = event_data.attr_name
    #     # tango://monctl.devk4.camlab.kat.ac.za:4000/mid_dish_0000/elt/
    #     # master/<attribute_name>#dbase=no
    #     # We process the FQDN of the attribute to extract just the
    #     # attribute name. Also handle the issue with the attribute name being
    #     # converted to lowercase in subsequent callbacks.
    #     attr_name = fqdn_attr_name.split("/")[-1].split("#")[0]
    #     log_message = f"{attr_name} is {event_data.attr_value.value}."
    #     self._read_activity_message = log_message
    #     self.logger.debug(log_message)

    # def convert_radec_to_azel(self, target, timestamp):
    #     """Converts RaDec coordinate in to AzEl coordinate using KATPoint library.

    #     :param target: str
    #         Argin to be provided is the Ra and Dec values in the following format:
    #         radec,21:08:47.92,89:15:51.4
    #     :param timestamp: str
    #         2020-12-11 10:06:34.970731
    #     :return: list
    #         Azimuth and elevation angle, in degrees
    #     :raises ValueError: If error occurs when creating katpoint Target or Timestamp.
    #     """
    #     device_data = DeviceData.get_instance()

    #     dish_antenna = katpoint.Antenna(
    #         name=device_data.dish_name,
    #         latitude=device_data.observer_location_lat,
    #         longitude=device_data.observer_location_long,
    #         altitude=device_data.observer_altitude,
    #     )

    #     dish_antenna_latitude = dish_antenna.ref_observer.lat
    #     try:
    #         desired_target = katpoint.Target(str(target))
    #         timestamp = katpoint.Timestamp(timestamp=timestamp)
    #         target_apparnt_radec = katpoint.Target.apparent_radec(
    #             desired_target, timestamp=timestamp, antenna=dish_antenna
    #         )
    #     except ValueError as value_err:
    #         self.logger.error(
    #             "Error creating instances of katpoint Target/Timestamp from target: '%s' and timestamp: '%s'.",
    #             target,
    #             timestamp,
    #         )
    #         raise value_err

    #     sidereal_time = dish_antenna.local_sidereal_time(timestamp=timestamp)
    #     sidereal_time_radian = katpoint.deg2rad(math.degrees(sidereal_time))

    #     # converting ra to ha
    #     hour_angle = sidereal_time_radian - target_apparnt_radec[0]

    #     # Geodetic latitude of the observer
    #     latitude_degree_decimal = UnitConverter().dms_to_dd(str(dish_antenna_latitude))
    #     latitude_radian = katpoint.deg2rad(latitude_degree_decimal)

    #     # Calculate enu coordinates
    #     enu_array = katpoint.hadec_to_enu(hour_angle, target_apparnt_radec[1], latitude_radian)

    #     # Calculate Az El coordinates
    #     az_el_coordinates = list(katpoint.enu_to_azel(enu_array[0], enu_array[1], enu_array[2]))
    #     az_el_coordinates[0] = katpoint.rad2deg(az_el_coordinates[0])
    #     az_el_coordinates[1] = katpoint.rad2deg(az_el_coordinates[1])
    #     return az_el_coordinates

    # def track_thread(self):
    #     """This thread writes coordinates to desiredPointing on DishMaster at the rate of 20 Hz."""
    #     self.logger.info(
    #         f"print track_thread thread name:{threading.currentThread().getName()}"
    #         f"{threading.get_ident()}"
    #     )
    #     device_data = DeviceData.get_instance()
    #     while device_data.event_track_time.is_set() is False:
    #         now = datetime.datetime.utcnow()
    #         timestamp = str(now)
    #         # pylint: disable=unbalanced-tuple-unpacking
    #         device_data.az, device_data.el = self.convert_radec_to_azel(device_data.radec_value, timestamp)

    #         if not self._is_elevation_within_mechanical_limits():
    #             time.sleep(0.05)
    #             continue

    #         if device_data.az < 0:
    #             device_data.az = 360 - abs(device_data.az)

    #         if device_data.event_track_time.is_set():
    #             log_message = f"Break loop: {device_data.event_track_time.is_set()}"
    #             self.logger.debug(log_message)
    #             break

    #         # TODO (kmadisa 11-12-2020) Add a pointing lead time to the current time (like we do on MeerKAT)
    #         desired_pointing = [now.timestamp(), round(device_data.az, 12), round(device_data.el, 12)]
    #         self.logger.debug("desiredPointing coordinates: %s", desired_pointing)
    #         self._dish_proxy.desiredPointing = desired_pointing

    #         time.sleep(0.05)

    # def _is_elevation_within_mechanical_limits(self):
    #     device_data = DeviceData.get_instance()
    #     if not (device_data.ele_min_lim <= device_data.el <= device_data.ele_max_lim):
    #         device_data.el_limit = True
    #         log_message = "Minimum/maximum elevation limit has been reached."
    #         self._read_activity_message = log_message
    #         self.logger.info(log_message)
    #         log_message = "Source is not visible currently."
    #         self._read_activity_message = log_message
    #         self.logger.info(log_message)
    #         return False

    #     device_data.el_limit = False
    #     return True

    def set_dish_name_number(self):
        device_data = DeviceData.get_instance()
        # Find out dish number from DishMasterFQDN property e.g. mid_d0001/elt/master
        dish_name_string = self.DishMasterFQDN.split("/")[0]
        device_data.dish_name = dish_name_string.split("_")[1]
        device_data.dish_number = device_data.dish_name[1:]

    def set_observer_lat_long_alt(self):
        # Load a set of antenna descriptions (latitude, longitude, altitude, enu coordinates)
        # from text file and construct Antenna objects from them. Currently the text file
        # contains Meerkat Antenna parameters.
        try:
            with importlib.resources.open_text("dishleafnode", "ska_antennas.txt") as f:
                descriptions = f.readlines()
            antennas = [katpoint.Antenna(line) for line in descriptions]
        except OSError as err:
            self.logger.error(err)
            raise err
        except ValueError as verr:
            self.logger.error(verr)
            raise verr

        antenna_exist = False

        device_data = DeviceData.get_instance()
        for ant in antennas:
            if ant.name == device_data.dish_number:
                ref_ant_lat = ant.ref_observer.lat
                ref_ant_long = ant.ref_observer.long
                ref_ant_altitude = ant.ref_observer.elevation
                ant_delay_model = ant.delay_model.values()
                antenna_exist = True
                break

        if not antenna_exist:
            raise Exception(f"Antenna '{device_data.dish_number}' not in the ska_antennas.txt file.")

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


        device_data.observer_location["latitude"] = f"{dish_lat_dms[0]}:{dish_lat_dms[1]}:{dish_lat_dms[2]}"
        device_data.observer_location["longitude"] = f"{dish_long_dms[0]}:{dish_long_dms[1]}:{dish_long_dms[2]}"
        device_data.observer_location["altitude"] = dish_ecef_coordinates[2]

    # def _get_targets(self, json_argument):
    #     try:
    #         ra_value = json_argument["pointing"]["target"]["RA"]
    #         dec_value = json_argument["pointing"]["target"]["dec"]
    #     except KeyError as key_error:
    #         tango.Except.throw_exception(
    #             str(key_error),
    #             "JSON key not found.",
    #             "_get_targets",
    #             tango.ErrSeverity.ERR,
    #         )

    #     return (ra_value, dec_value)

    # def _load_config_string(self, argin):
    #     try:
    #         json_argument = json.loads(argin)
    #     except json.JSONDecodeError as jsonerr:
    #         tango.Except.throw_exception(
    #             str(jsonerr),
    #             "Invalid JSON format.",
    #             "_load_config_string",
    #             tango.ErrSeverity.ERR,
    #         )

    #     return json_argument

    # -----------------
    # Device Properties
    # -----------------
    DishMasterFQDN = device_property(
        dtype="str",
        default_value="mid_d0001/elt/master",
        doc="FQDN of Dish Master Device",
    )

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
        return self.device_data._read_activity_message

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage """
        self.device_data._read_activity_message = value

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

            :return: A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.
            :rtype: (ResultCode, str)
            :raises DevFailed: If error occurs in creating a DeviceProxy instance for DishMaster
            """

            super().do()
            device = self.target

            this_server = TangoServerHelper.get_instance()
            this_server.device = device

            self.logger.info("Initializing DishLeafNode...")
            # Create DeviceData class instance
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            device_data._dish_master_fqdn = device.DishMasterFQDN
            # device.el = 30.0
            # device.az = 0.0
            # device.ele_max_lim = 90
            # device.ele_min_lim = 17.5
            # device.el_limit = False
            device._build_state = f"{release.name},{release.version},{release.description}"
            device._version_id = release.version
            # device.radec_value = ""
            device.set_dish_name_number()
            device.set_observer_lat_long_alt()
            log_message = f"DishMasterFQDN :-> {device.DishMasterFQDN}"
            self.logger.debug(log_message)
            device_data._read_activity_message = log_message
            # device.event_track_time = threading.Event()
            device._health_state = HealthState.OK
            device._simulation_mode = SimulationMode.FALSE


            # try:
            #     device._dish_proxy = DeviceProxy(str(device.DishMasterFQDN))
            # except DevFailed as dev_failed:
            #     self.logger.exception(dev_failed)
            #     log_message = "Error in creating proxy to the Dish Master"
            #     device._read_activity_message = log_message
            #     tango.Except.re_throw_exception(
            #         dev_failed,
            #         "Exception in Init command",
            #         log_message,
            #         "DishLeafNode.{}Command".format("Init"),
            #         tango.ErrSeverity.ERR,
            #     )

            # attributes_to_subscribe_to = (
            #     "dishMode",
            #     "capturing",
            #     "achievedPointing",
            #     "desiredPointing",
            # )

            # self._subscribe_to_attribute_events(attributes_to_subscribe_to)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_message = (
                f"Setting CallBack Model as :-> {ApiUtil.instance().get_asynch_cb_sub_model()}"
            )
            self.logger.debug(log_message)
            device_data._read_activity_message = log_message
            log_message = "Dish Leaf Node initialized successfully."
            device.set_status(log_message)
            device_data._read_activity_message = log_message
            self.logger.info(log_message)
            return (ResultCode.OK, device_data._read_activity_message)

        # def _subscribe_to_attribute_events(self, attributes):
        #     device = self.target
        #     for attribute_name in attributes:
        #         try:
        #             device._dish_proxy.subscribe_event(
        #                 attribute_name,
        #                 EventType.CHANGE_EVENT,
        #                 device.attribute_event_handler,
        #                 stateless=True,
        #             )
        #         except DevFailed as dev_failed:
        #             self.logger.exception(dev_failed)
        #             log_message = (
        #                 f"Exception occurred while subscribing to Dish attribute: {attribute_name}"
        #             )
        #             device.set_status("Error occured in Dish Leaf Node initialization")
        #             device_data._read_activity_message = log_message
        #             tango.Except.re_throw_exception(
        #                 dev_failed,
        #                 "Exception in Init command",
        #                 log_message,
        #                 "DishLeafNode.{}Command".format("Init"),
        #                 tango.ErrSeverity.ERR,
        #             )

    @command()
    def SetStowMode(self):
        """Invokes SetStowMode command on DishMaster."""
        handler = self.get_command_object("SetStowMode")
        handler()


    @command()
    def SetStandbyLPMode(self):
        """Invokes SetStandbyLPMode (i.e. Low Power State) command on DishMaster."""
        handler = self.get_command_object("SetStandbyLPMode")
        handler()

    @command()
    def SetOperateMode(self):
        """Invokes SetOperateMode command on DishMaster."""
        handler = self.get_command_object("SetOperateMode")
        handler()

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
        """Invokes Scan command on DishMaster."""
        handler = self.get_command_object("Scan")
        handler(argin)


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
        """Invokes StopCapture command on DishMaster."""
        handler = self.get_command_object("EndScan")
        handler(argin)

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
        """Configures the Dish by setting pointing coordinates for a given observation."""
        handler = self.get_command_object("Configure")
        handler(argin)

    
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
        """Triggers the DishMaster to Start capture on the set configured band."""
        handler = self.get_command_object("StartCapture")
        handler(argin)


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
        """Invokes StopCapture command on DishMaster on the set configured band."""
        handler = self.get_command_object("StopCapture")
        handler(argin)


    @command()
    def SetStandbyFPMode(self):
        """Invokes SetStandbyFPMode command on DishMaster (Standby-Full power) mode."""
        handler = self.get_command_object("SetStandbyFPMode")
        handler()


    def is_Slew_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.
        :rtype: boolean
        """
        handler = self.get_command_object("Slew")
        return handler.check_allowed()

    @command(
        dtype_in="DevVarDoubleArray",
        doc_in="[Azimuth, Elevation] all in degrees",
    )
    def Slew(self, argin):
        """
        Invokes Slew command on DishMaster to slew the dish towards the set pointing coordinates.
        """
        handler = self.get_command_object("Slew")
        handler(argin)


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
        """Invokes Track command on the DishMaster."""
        handler = self.get_command_object("Track")
        handler(argin)

    
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
        """Invokes StopTrack command on the DishMaster."""
        handler = self.get_command_object("StopTrack")
        handler()


    @command()
    def Abort(self):
        """Invokes Abort command on the DishMaster."""
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

    
    @command()
    def Restart(self):
        """Invokes Restart command on the DishMaster."""
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


    @command()
    def ObsReset(self):
        """Invokes ObsReset command on the DishLeafNode."""
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
