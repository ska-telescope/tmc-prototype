"""
MCCS Subarray Leaf node monitors the MCCS Subarray and issues control actions during an observation.
It also acts as a MCCS contact point for Subarray Node for observation execution for TMC.
"""
# -*- coding: utf-8 -*-
#
# This file is part of the MccsSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(MccSubarrayLeafNode.additional_import) ENABLED START #

# Third party imports
import threading
# Tango imports
from tango import DebugIt, AttrWriteType
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState

from tmc.common.tango_server_helper import TangoServerHelper

from .device_data import DeviceData
from . import const, release
from .configure_command import Configure
from .scan_command import Scan
from .end_command import End
from .end_scan_command import EndScan
from .abort_command import Abort
from .obsreset_command import ObsReset

__all__ = [
    "MccsSubarrayLeafNode",
    "main",
    "Configure",
    "Scan",
    "EndScan",
    "End",
    "Abort",
    "ObsReset",
]
# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import


class MccsSubarrayLeafNode(SKABaseDevice):
    """
    MCCS Subarray Leaf node monitors the MCCS Subarray and issues control actions during an observation.

    :Device Properties:

        MccsSubarrayFQDN:
            FQDN of MCCS Subarray.

    :Device Attributes:

        mccsSubarrayHealthState:
            Forwarded attribute to provide MCCS Subarray Health State.

        mccsSubarrayObsState:
            Attribute to provide MCCS Subarray Observation State.

        activityMessage:
            String providing information about the current activity in MCCS Subarray Leaf Node.

    """

    # -----------------
    # Device Properties
    # -----------------

    MccsSubarrayFQDN = device_property(
        dtype="str", default_value="low-mccs/subarray/01"
    )

    # ----------
    # Attributes
    # ----------

    activityMessage = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
    )

    mccsSubarrayHealthState = attribute(
        name="mccsSubarrayHealthState", label="mccsSubarrayHealthState", forwarded=True
    )
    mccsSubarrayObsState = attribute(
        name="mccsSubarrayObsState", label="mccsSubarrayObsState", forwarded=True
    )
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the MccsSubarrayLeafNode's init_device() method"
        """

        def do(self):
            """
            Initializes the attributes and properties of the MccsSubarrayLeafNode.

            return:
                A tuple containing a return code and a string message indicating status. The message is
                for information purpose only.

            rtype:
                (ReturnCode, str)

            raises:
                DevFailed if error occurs in creating proxy for MCCSSubarray.

            """
            super().do()
            device = self.target
            this_server = TangoServerHelper.get_instance()
            this_server.set_tango_class(device)
            device.attr_map = {}
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            device._build_state = "{},{},{}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version
            device._versioninfo = " "
            device.set_status(const.STR_MCCSSALN_INIT_SUCCESS)
            device._mccs_subarray_health_state = HealthState.OK
            self.logger.info(const.STR_MCCSSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_MCCSSALN_INIT_SUCCESS)

    def always_executed_hook(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activityMessage_read) ENABLED START #
        return self.attr_map["activityMessage"]
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activityMessage_write) ENABLED START #
        self.update_attr_map("activityMessage", value)
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activityMessage_write

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

    def is_Configure_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        return:
            True if this command is allowed to be run in
            current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run
            in current device state

        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(dtype_in=("str"))
    @DebugIt()
    def Configure(self, argin):
        """ Invokes Configure command on MccsSubarrayLeafNode """
        handler = self.get_command_object("Configure")
        handler(argin)

    @command(dtype_in=("str"))
    @DebugIt()
    def Scan(self, argin):
        """ Invokes Scan command on mccssubarrayleafnode"""
        handler = self.get_command_object("Scan")
        handler(argin)

    def is_Scan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        return:
            True if this command is allowed to be run in
            current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run
            in current device state

        """
        handler = self.get_command_object("Scan")
        return handler.check_allowed()

    @command()
    def EndScan(self):
        """ Invokes EndScan command on MccsSubarray."""
        handler = self.get_command_object("EndScan")
        handler()

    def is_EndScan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state.

        return:
            True if this command is allowed to be run in
            current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run
            in current device state

        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    def is_End_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        return:
            True if this command is allowed to be run in
            current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run
            in current device state

        """
        handler = self.get_command_object("End")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def End(self):
        """ Invokes End command on MccsSubarrayLeafNode. """
        handler = self.get_command_object("End")
        handler()

    def is_Abort_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        return:
            True if this command is allowed to be run in
            current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run
            in current device state

        """
        handler = self.get_command_object("Abort")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def Abort(self):
        """ Invokes Abort command on MccsSubarrayLeafNode. """
        handler = self.get_command_object("Abort")
        handler()

    def is_ObsReset_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        return:
            True if this command is allowed to be run in
            current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run
            in current device state

        """
        handler = self.get_command_object("ObsReset")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def ObsReset(self):
        """ Invokes ObsReset command on MccsSubarrayLeafNode. """
        handler = self.get_command_object("ObsReset")
        handler()

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self.device_data, self.state_model, self.logger)
        self.configure = Configure(*args)
        self.scan = Scan(*args)
        self.endscan = EndScan(*args)
        self.end = End(*args)
        self.abort = Abort(*args)
        self.obsreset = ObsReset(*args)

        # are registered and inherited from SKASubarray
        self.register_command_object("Configure", self.configure)
        self.register_command_object("Scan", self.scan)
        self.register_command_object("EndScan", self.endscan)
        self.register_command_object("End", self.end)
        self.register_command_object("Abort", self.abort)
        self.register_command_object("ObsReset", self.obsreset)


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsSubarrayLeafNode.main) ENABLED START #
    return run((MccsSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.main


if __name__ == "__main__":
    main()
