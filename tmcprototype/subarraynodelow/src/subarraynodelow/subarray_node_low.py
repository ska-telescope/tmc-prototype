# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Subarray Node
Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a Subarray.
"""

# PROTECTED REGION ID(SubarrayNode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property
from . import const, release, on_command, off_command
from .const import PointingState
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, ObsMode, ObsState
from ska.base import SKASubarray
from subarraynode.exceptions import InvalidObsStateError

__all__ = ["SubarrayNode", "main", "on_command", "off_command"]


class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START #
    def command_class_object(self):
        """
        Sets up the command objects
        :return: None
        """
        args = (self, self.state_model, self.logger)
        self.init_obj = self.InitCommand(*args)
        self.on_obj = on_command.OnCommand(*args)
        self.off_obj = off_command.OffCommand(*args)


    def get_deviceproxy(self, device_fqdn):
        """
        Returns device proxy for given FQDN.
        """
        retry = 0
        device_proxy = None
        while retry < 3:
            try:
                device_proxy = DeviceProxy(device_fqdn)
                break
            except DevFailed as df:
                self.logger.exception(df)
                if retry >= 2:
                    tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                    "Failed to create DeviceProxy of " + str(device_fqdn),
                                                    "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                retry += 1
                continue
        return device_proxy

    # -----------------
    # Device Properties
    # -----------------

    DishLeafNodePrefix = device_property(
        dtype='str', doc="Device name prefix for the Dish Leaf Node",
    )

    CspSubarrayLNFQDN = device_property(

        dtype='str', doc="This property contains the FQDN of the CSP Subarray Leaf Node associated with the "
            "Subarray Node.",
    )

    SdpSubarrayLNFQDN = device_property(
        dtype='str', doc="This property contains the FQDN of the SDP Subarray Leaf Node associated with the "
            "Subarray Node.",
    )

    CspSubarrayFQDN = device_property(
        dtype='str',
    )

    SdpSubarrayFQDN = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype='str',
        doc="ID of ongoing SCAN",
    )

    sbID = attribute(
        dtype='str',
        doc="ID of ongoing Scheduling Block",
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    receptorIDList = attribute(
        dtype=('uint16',),
        max_dim_x=100,
        doc="ID List of the Receptors assigned in the Subarray",
    )

    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKASubarray.InitCommand):
        """
        A class for the TMC SubarrayNode's init_device() method.
        """
        def do(self):
            """
            Initializes the attributes and properties of the Subarray Node.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the error while subscribing the tango attribute
            """
            super().do()
            device = self.target
            device.set_status(const.STR_SA_INIT)
            device._obs_mode = ObsMode.IDLE
            device._scan_id = ""
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._health_event_id = []
            device.subarray_ln_health_state_map = {}
            device._subarray_health_state = HealthState.OK  #Aggregated Subarray Health State

            # Create proxy for CSP Subarray Leaf Node
            device._mccs_subarray_ln_proxy = None
            device._mccs_subarray_ln_proxy = device.get_deviceproxy(device.MccsSubarrayLNFQDN)
            device.command_class_object()
            device._read_activity_message = const.STR_SA_INIT_SUCCESS
            self.logger.info(device._read_activity_message)
            return (ResultCode.OK, device._read_activity_message)

    def always_executed_hook(self):
        """ Internal construct of TANGO. """
        # PROTECTED REGION ID(SubarrayNode.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SubarrayNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SubarrayNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        """ Internal construct of TANGO. Returns the Scan ID.

        EXAMPLE: 123
        Where 123 is a Scan ID from configuration json string.
        """
        # PROTECTED REGION ID(SubarrayNode.scanID_read) ENABLED START #
        return self._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_activityMessage(self):
        """ Internal construct of TANGO. Returns activityMessage.
        Example: "Subarray node is initialized successfully"
        //result occured after initialization of device.
        """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    def read_receptorIDList(self):
        """ Internal construct of TANGO. Returns the receptor IDs allocated to the Subarray.
         """
        # PROTECTED REGION ID(SubarrayNode.receptorIDList_read) ENABLED START #
        return self._receptor_id_list
        # PROTECTED REGION END #    //  SubarrayNode.receptorIDList_read

    # --------
    # Commands
    # --------

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("On", on_command.OnCommand(*args))
        self.register_command_object("Off", off_command.OffCommand(*args))

# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(SubarrayNode.main) ENABLED START #
    """
    Runs the SubarrayNode.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: SubarrayNode TANGO object.
    """
    return run((SubarrayNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SubarrayNode.main

if __name__ == '__main__':
    main()