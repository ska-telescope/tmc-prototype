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
from tango import AttrWriteType
from tango.server import run,attribute, command, device_property

# Additional imports
from . import const, release,  track_command
from ska.base.commands import ResultCode
from ska.base.control_model import ObsMode
from ska.base import SKASubarray
from subarraynode.device_data import DeviceData
from subarraynode.on_command import On
from subarraynode.off_command import Off
from subarraynode.assign_resources_command import AssignResources
from subarraynode.release_all_resources_command import ReleaseAllResources
from subarraynode.configure_command import Configure
from subarraynode.scan_command import Scan
from subarraynode.end_scan_command import EndScan
from subarraynode.end_command import End
from subarraynode.abort_command import Abort
from subarraynode.restart_command import Restart
from subarraynode.obsreset_command import ObsReset
from subarraynode.track_command import Track
from tmc.common.tango_server_helper import TangoServerHelper

__all__ = ["SubarrayNode", "main", "AssignResources", "ReleaseAllResources",
           "Configure", "Scan", "EndScan", "End", "On",
           "Off", "Track", "Abort", "Restart", "ObsReset"]


class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.

    :Device Properties:

        SdpSubarrayLNFQDN:
            This property contains the FQDN of the SDP Subarray Leaf Node associated with the
            Subarray Node.

        CspSubarrayLNFQDN:
            This property contains the FQDN of the CSP Subarray Leaf Node associated with the
            Subarray Node.

        DishLeafNodePrefix:
            Device name prefix for the Dish Leaf Node.

        CspSubarrayFQDN:
            FQDN of the CSP Subarray Tango Device Server.

        SdpSubarrayFQDN:
            FQDN of the CSP Subarray Tango Device Server.

    :Device Attributes:

        scanID:
            ID of ongoing SCAN

        sbID:
            ID of ongoing Scheduling Block

        activityMessage:
            String providing information about the current activity in SubarrayNode.

        receptorIDList:
            ID List of the Receptors assigned in the Subarray.

    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START

    # PROTECTED REGION END #    //  SubarrayNode.class_variable

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

            return:
                A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.

            rtype:
                (ReturnCode, str)

            raises:
                DevFailed if the error while subscribing the tango attribute
            """
            super().do()
            device = self.target
            # TODO: get Tangoserver instance
            this_server = TangoServerHelper.get_instance()
            this_server.device = device

            device.set_status(const.STR_SA_INIT)
            device._obs_mode = ObsMode.IDLE
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device.scan_thread = None
            # Step 1: Create object of configuration model
            device.device_data = DeviceData.get_instance()
            device.device_data._read_activity_message = const.STR_SA_INIT_SUCCESS
            device.device_data.sdp_subarray_ln_fqdn = device.SdpSubarrayLNFQDN
            device.device_data.csp_subarray_ln_fqdn = device.CspSubarrayLNFQDN
            device.device_data.dish_leaf_node_prefix = device.DishLeafNodePrefix
            device.device_data.csp_sa_fqdn = device.CspSubarrayFQDN
            device.device_data.sdp_sa_fqdn = device.SdpSubarrayFQDN
            return (ResultCode.OK, device.device_data._read_activity_message)

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
        return self.device_data._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_sbID(self):
        """ Internal construct of TANGO. Returns the scheduling block ID. """
        # PROTECTED REGION ID(SubarrayNode.sbID_read) ENABLED START #
        return self.device_data._sb_id
        # PROTECTED REGION END #    //  SubarrayNode.sbID_read

    def read_activityMessage(self):
        """ Internal construct of TANGO. Returns activityMessage.
        Example: "Subarray node is initialized successfully"
        //result occured after initialization of device.
        """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self.device_data._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self.device_data._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    def read_receptorIDList(self):
        """ Internal construct of TANGO. Returns the receptor IDs allocated to the Subarray.
         """
        # PROTECTED REGION ID(SubarrayNode.receptorIDList_read) ENABLED START #
        return self.device_data._receptor_id_list
        # PROTECTED REGION END #    //  SubarrayNode.receptorIDList_read

    # --------
    # Commands
    # --------

    def is_Track_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Track")
        return handler.check_allowed()

    @command(
        dtype_in='str',
        doc_in="Initial Pointing parameters of Dish - Right Ascension and Declination coordinates.",
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def Track(self, argin):
        """
        Invokes Track command on the Dishes assigned to the Subarray.
        """
        handler = self.get_command_object("Track")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.configure = Configure(*args)
        self.assign = AssignResources(*args)
        self.release = ReleaseAllResources(*args)
        self.scan = Scan(*args)
        self.endscan = EndScan(*args)
        self.end = End(*args)
        self.restart = Restart(*args)
        self.abort = Abort(*args)
        self.on = On(*args)
        self.off = Off(*args)
        self.obsreset = ObsReset(*args)
        self.track = Track(*args)

        self.register_command_object("Track", track_command.Track(*args))
        # In order to pass self = subarray node as target device, the assign and release resource commands
        # are registered and inherited from SKASubarray
        self.register_command_object("AssignResources", self.assign)
        self.register_command_object("ReleaseAllResources", self.release)
        self.register_command_object("Configure", self.configure)
        self.register_command_object("Scan", self.scan)
        self.register_command_object("EndScan", self.endscan)
        self.register_command_object("End", self.end)
        self.register_command_object("On", self.on)
        self.register_command_object("Off", self.off)
        self.register_command_object("Abort", self.abort)
        self.register_command_object("Restart", self.restart)
        self.register_command_object("ObsReset", self.obsreset)
        self.register_command_object("Track", self.track)

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
