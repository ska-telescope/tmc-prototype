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
import threading
# Tango imports
import tango
from tango import ApiUtil, AttrWriteType
from tango.server import run, command, device_property, attribute

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, SimulationMode

from tmc.common.tango_server_helper import TangoServerHelper

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


__all__ = [
    "DishLeafNode",
    "main",
    "release",
    "SetOperateMode",
    "SetStandbyLPMode",
    "SetStandbyFPMode",
    "SetStowMode",
    "Scan",
    "EndScan",
    "StartCapture",
    "StopCapture",
    "Abort",
    "Restart",
    "ObsReset",
    "Slew",
    "Configure",
    "Track",
    "StopTrack",
]

# pylint: disable=unused-variable, logging-fstring-interpolation
class DishLeafNode(SKABaseDevice):
    """
    A Leaf control node for DishMaster.

    :Device Properties:

        DishMasterFQDN:
            FQDN of Dish Master Device

    :Device Attributes:

        activityMessage:
            String providing information about the current activity in DishLeaf Node.

        dishHealthState:
            Forwarded attribute to provide Dish Master Health State

        dishPointingState:
            Forwarded attribute to provide Dish Master Pointing State

    """

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
        return self.attr_map["activityMessage"]

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage """
        self.update_attr_map("activityMessage", value)

    def update_attr_map(self, attr, val):
        """
        This method updates attribute value in attribute map. Once a thread has acquired a lock,
        subsequent attempts to acquire it are blocked, until it is released.
        """
        lock = threading.Lock()
        lock.acquire()
        self.attr_map[attr] = val
        lock.release()

    dishHealthState = attribute(
        name="dishHealthState", label="dishHealthState", forwarded=True
    )

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
            self.logger.info("Initializing DishLeafNode...")
            # Create DeviceData class instance
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            # Get Instance of TangoServerHelper class
            this_server = TangoServerHelper.get_instance()
            this_server.device = device
            device.attr_map = {}
            # Initialise Attributes
            device.attr_map["activityMessage"] = ""
            device._build_state = (
                f"{release.name},{release.version},{release.description}"
            )
            device._version_id = release.version
            device_data.set_dish_name_number()
            device_data.set_observer_lat_long_alt(self.logger)
            log_message = f"DishMasterFQDN :-> {device.DishMasterFQDN}"
            self.logger.debug(log_message)
            this_server.write_attr("activityMessage", log_message)
            device._health_state = HealthState.OK
            device._simulation_mode = SimulationMode.FALSE

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_message = f"Setting CallBack Model as :-> {ApiUtil.instance().get_asynch_cb_sub_model()}"
            self.logger.debug(log_message)
            this_server.write_attr("activityMessage", log_message)
            log_message = "Dish Leaf Node initialized successfully."
            device.set_status(log_message)
            this_server.write_attr("activityMessage", log_message)
            self.logger.info(log_message)
            return (ResultCode.OK, device.attr_map["activityMessage"])

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
