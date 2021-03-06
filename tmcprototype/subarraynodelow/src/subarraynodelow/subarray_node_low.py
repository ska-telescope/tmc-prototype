# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Subarray Node Low
Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a Subarray.
"""
# Tango imports
from tango import AttrWriteType
from tango.server import run,attribute, device_property

# Additional imports
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, ObsMode, ObsState
from ska.base import SKASubarray
from .device_data import DeviceData
from tmc.common.tango_server_helper import TangoServerHelper
from . import const, release 
from .on_command import On
from .off_command import Off
from .assign_resources_command import AssignResources
from .configure_command import Configure
from .scan_command import Scan
from .end_command import End
from .end_scan_command import EndScan
from .release_all_resources_command import ReleaseAllResources
from .abort_command import Abort
from .obsreset_command import ObsReset

__all__ = ["SubarrayNode", "main", "AssignResources", "ReleaseAllResources",
           "Configure", "Scan", "EndScan", "End", "On", "ObsReset", "Abort", "Off"]



class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # -----------------
    # Device Properties
    # -----------------

    MccsSubarrayLNFQDN = device_property(
        dtype='str', doc="This property contains the FQDN of the MCCS Subarray Leaf Node associated with the "
                         "Subarray Node."
    )

    MccsSubarrayFQDN = device_property(
        dtype='str', doc="This property contains the FQDN of the MCCS Subarray associated with the "
                         "Subarray Node."
    )

    MccsSubarrayFQDN = device_property(
        dtype='str',
    )


    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype='str',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
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
            device_data = DeviceData.get_instance()
            device.device_data = device_data

            this_server = TangoServerHelper.get_instance()
            this_server.device = device

            device._obs_mode = ObsMode.IDLE
            device._scan_id = ""
            device._resource_list = []
            device.is_end_command = False
            device.is_release_resources = False
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._health_event_id = []
            device._mccs_sa_obs_state = ObsState.EMPTY
            device.subarray_ln_health_state_map = {}
            device._subarray_health_state = HealthState.OK  #Aggregated Subarray Health State
            device_data.mccs_subarray_fqdn = device.MccsSubarrayFQDN
            device_data.mccs_subarray_ln_fqdn = device.MccsSubarrayLNFQDN

            device_data.activity_message = const.STR_SA_INIT_SUCCESS
            self.logger.info(device_data.activity_message)
            return (ResultCode.OK, device_data.activity_message)

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
        return self.device_data.activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self.device_data.activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    # --------
    # Commands
    # --------
    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()

        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.on = On(*args)
        self.off = Off(*args)
        self.end = End(*args)
        self.scan = Scan(*args)
        self.endscan = EndScan(*args)
        self.configure = Configure(*args)
        self.release = ReleaseAllResources(*args)
        self.assign = AssignResources(*args)
        self.obsreset = ObsReset(*args)
        self.abort = Abort(*args)
        
        self.register_command_object("AssignResources", self.assign)
        self.register_command_object("ReleaseAllResources", self.release)
        self.register_command_object("On", self.on)
        self.register_command_object("Off", self.off)
        self.register_command_object("Configure", self.configure)
        self.register_command_object("Scan", self.scan)
        self.register_command_object("End", self.end)
        self.register_command_object("EndScan", self.endscan)
        self.register_command_object("ObsReset", self.endscan)
        self.register_command_object("Abort", self.abort)

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