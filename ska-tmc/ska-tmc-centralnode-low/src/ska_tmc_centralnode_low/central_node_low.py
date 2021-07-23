# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""
Central Node is a coordinator of the complete M&C system. Central Node implements the standard set
of state and mode attributes defined by the SKA Control Model.
"""

# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import threading
# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DevFailed
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState
from tmc.common.tango_server_helper import TangoServerHelper
from . import const, release
from .device_data import DeviceData
from .startup_telescope_command import StartUpTelescope
from .standby_telescope_command import StandByTelescope
from .assign_resources_command import AssignResources
from .release_resources_command import ReleaseResources

# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = [
    "CentralNode",
    "main",
    "AssignResources",
    "ReleaseResources",
    "StandByTelescope",
    "StartUpTelescope",
]


class CentralNode(SKABaseDevice):
    """
    Central Node is a coordinator of the complete M&C system.

    :Device Properties:

        CentralAlarmHandler:
            Device name of CentralAlarmHandler

        TMAlarmHandler:
            Device name of TMAlarmHandler

        TMLowSubarrayNodes:
            List of TM Low Subarray Node devices

        MCCSMasterLeafNodeFQDN:
            FQDN of Mccs Master Leaf Node.

    :Device Attributes:

        telescopeHealthState:
            Health state of Telescope

        subarray1HealthState:
            Health state of SubarrayNode1

        activityMessage:
            String providing information about the current activity in Central Node.

    """

    # -----------------
    # Device Properties
    # -----------------
    CentralAlarmHandler = device_property(
        dtype="str",
        doc="Device name of CentralAlarmHandler ",
    )

    TMAlarmHandler = device_property(
        dtype="str",
        doc="Device name of TMAlarmHandler ",
    )

    TMLowSubarrayNodes = device_property(
        dtype=("str",),
        doc="List of TM Low Subarray Node devices",
    )

    MCCSMasterLeafNodeFQDN = device_property(dtype="str")

    # ----------
    # Attributes
    # ----------

    telescopeHealthState = attribute(
        dtype=HealthState,
        doc="Health state of Telescope",
    )

    subarray1HealthState = attribute(
        dtype=HealthState,
        doc="Health state of Subarray1",
    )

    activityMessage = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )


    # ---------------
    # General methods
    # ---------------
    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC CentralNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the Central Node Low.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs while initializing the CentralNode device or if error occurs while
                    creating device proxy for any of the devices like SubarrayNodeLow or MccsMasterLeafNode.

            """
            super().do()

            device = self.target
            try:
                self.logger.info("Device initialisating...")
                device_data = DeviceData.get_instance()
                device.device_data = device_data
                # Get Instance of TangoServerHelper class
                this_server = TangoServerHelper.get_instance()
                this_server.set_tango_class(device)
                device.attr_map = {}
                # Initialise Attributes
                device.attr_map["telescopeHealthState"]=HealthState.UNKNOWN
                device.attr_map["subarray1HealthState"]=HealthState.UNKNOWN
                device.attr_map["activityMessage"]=""

                device._health_state = HealthState.OK
                device._build_state = "{},{},{}".format(
                    release.name, release.version, release.description
                )
                device._version_id = release.version
                device_data.mccs_controller_fqdn = "low-mccs/control/control"
                self.logger.debug(const.STR_INIT_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = f"{const.ERR_INIT_PROP_ATTR_CN}{dev_failed}"
                self.logger.exception(dev_failed)
                this_server.write_attr("activityMessage", const.ERR_INIT_PROP_ATTR_CN, False)
                tango.Except.throw_exception(
                    const.STR_CMD_FAILED,
                    log_msg,
                    "CentralNode.InitCommand.do()",
                    tango.ErrSeverity.ERR,
                )

            for subarray in range(0, len(device.TMLowSubarrayNodes)):
                # populate subarray_id-subarray proxy map
                tokens = device.TMLowSubarrayNodes[subarray].split("/")
                subarray_id = int(tokens[2])
                device_data.subarray_FQDN_dict[subarray_id] = device.TMLowSubarrayNodes[
                    subarray
                ]

            this_server.write_attr("activityMessage", const.STR_CN_INIT_SUCCESS, False)
            self.logger.info(device.attr_map["activityMessage"])
            return (ResultCode.OK, device.attr_map["activityMessage"])

    def always_executed_hook(self):
        # PROTECTED REGION ID(CentralNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CentralNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CentralNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CentralNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_telescopeHealthState(self):
        # PROTECTED REGION ID(CentralNode.telescope_healthstate_read) ENABLED START #
        """ Internal construct of TANGO. Returns the Telescope health state."""
        return self.attr_map["telescopeHealthState"]
        # PROTECTED REGION END #    //  CentralNode.telescope_healthstate_read

    def read_subarray1HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray1_healthstate_read) ENABLED START #
        """ Internal construct of TANGO. Returns Subarray1 health state. """
        return self.attr_map["subarray1HealthState"]
        # PROTECTED REGION END #    //  CentralNode.subarray1_healthstate_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CentralNode.activity_message_read) ENABLED START #
        """Internal construct of TANGO. Returns activity message. """
        return self.attr_map["activityMessage"]
        # PROTECTED REGION END #    //  CentralNode.activity_message_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CentralNode.activity_message_write) ENABLED START #
        """Internal construct of TANGO. Sets the activity message. """
        self.update_attr_map("activityMessage", value)
        # PROTECTED REGION END #    //  CentralNode.activity_message_write

    def update_attr_map(self, attr, val):
        """
        This method updates attribute value in attribute map. Once a thread has acquired a lock,
        subsequent attempts to acquire it are blocked, until it is released.
        """
        lock = threading.Lock()
        lock.acquire()
        self.attr_map[attr] = val
        lock.release()

    # --------
    # Commands
    # --------
    def is_StandByTelescope_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("StandByTelescope")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StandByTelescope(self):
        """
        This command invokes Off() command on SubarrayNode, MCCSMasterLeafNode and sets CentralNode into OFF state.

        """
        handler = self.get_command_object("StandByTelescope")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_StartUpTelescope_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("StartUpTelescope")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def StartUpTelescope(self):
        """
        This command invokes On() command on SubarrayNode, MCCSMasterLeafNode
        and sets the Central Node into ON state.
        """
        handler = self.get_command_object("StartUpTelescope")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_AssignResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="It accepts the subarray id, station ids, station beam id and channels in JSON string format",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        AssignResources command invokes the AssignResources command on lower level devices.
        """
        handler = self.get_command_object("AssignResources")
        handler(argin)

    def is_ReleaseResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("ReleaseResources")
        return handler.check_allowed()

    @command(
        dtype_in="str",
        doc_in="The string in JSON format. The JSON contains following values:\nsubarray_id: "
        "and release_all boolean as true.",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Release all the resources assigned to the given Subarray.
        """
        handler = self.get_command_object("ReleaseResources")

        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        args = (self.device_data, self.state_model, self.logger)
        self.assign_resources = AssignResources(*args)
        self.release_resources = ReleaseResources(*args)
        self.startup_telescope = StartUpTelescope(*args)
        self.standby_telescope = StandByTelescope(*args)

        self.register_command_object("StartUpTelescope", self.startup_telescope)
        self.register_command_object("StandByTelescope", self.standby_telescope)
        self.register_command_object("AssignResources", self.assign_resources)
        self.register_command_object("ReleaseResources", self.release_resources)


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CentralNode.main) ENABLED START #
    """
    Runs the CentralNode.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: CentralNode TANGO object.
    """
    return run((CentralNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CentralNode.main


if __name__ == "__main__":
    main()
