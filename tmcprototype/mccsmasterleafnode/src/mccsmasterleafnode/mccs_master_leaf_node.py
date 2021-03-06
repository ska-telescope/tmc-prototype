# -*- coding: utf-8 -*-
#
# This file is part of the MccsMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Tango imports
import tango
from tango import ApiUtil, DebugIt, AttrWriteType
from tango.server import run, command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, SimulationMode, TestMode
from . import const, release
from .assign_resources_command import AssignResources
from .release_resources_command import ReleaseResources
from .on_command import On
from .off_command import Off
from .device_data import DeviceData

# PROTECTED REGION END #    //  MccsMasterLeafNode imports

__all__ = ["MccsMasterLeafNode", "main", "AssignResources", "const", 
           "release", "ReleaseResources", "On", "Off"]

class MccsMasterLeafNode(SKABaseDevice):
    """
    **Properties:**

    - MccsMasterFQDN   - Property to provide FQDN of MCCS Master Device

    **Attributes:**

    - mccsHealthState  - Forwarded attribute to provide MCCS Master Health State
    - activityMessage - Attribute to provide activity message

    """

    # -----------------
    # Device Properties
    # -----------------

    MccsMasterFQDN = device_property(
        dtype='str', default_value="low-mccs/control/control"
    )
    # ----------
    # Attributes
    # ----------

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    mccsHealthState = attribute(name="mccsHealthState", label="mccsHealthState", forwarded=True)
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC MCCS Master Leaf Node's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the MccsMasterLeafNode.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while creating the device proxy for Mccs Master or
                    subscribing the evennts.
            """
            super().do()
            device = self.target
            device._health_state = HealthState.OK  # Setting healthState to "OK"
            device._simulation_mode = SimulationMode.FALSE  # Enabling the simulation mode
            device._test_mode = TestMode.NONE
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version

            # Create DeviceData class instance
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            device_data._read_activity_message = const.STR_MCCS_INIT_LEAF_NODE
            device_data._read_activity_message = const.STR_MCCSMASTER_FQDN + str(device.MccsMasterFQDN)
            # Creating proxy to the CSPMaster
            log_msg = "MCCS Master name: " + str(device.MccsMasterFQDN)
            self.logger.debug(log_msg)
            device_data._mccs_master_fqdn = str(device.MccsMasterFQDN)
        
            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            self.logger.debug(log_msg)
            device_data._read_activity_message = const.STR_INIT_SUCCESS
            self.logger.info(device_data._read_activity_message)
            return (ResultCode.OK, device_data._read_activity_message)

    def always_executed_hook(self):
        # PROTECTED REGION ID(MccsMasterLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MccsMasterLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(MccsMasterLeafNode.activityMessage_read) ENABLED START #
        return self.device_data._read_activity_message
        # PROTECTED REGION END #    //  MccsMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(MccsMasterLeafNode.activityMessage_write) ENABLED START #
        self.device_data._read_activity_message = value
        # PROTECTED REGION END #    //  MccsMasterLeafNode.activityMessage_write

                                                 
    @command(
        dtype_in='str',
    )
    @DebugIt()
    def AssignResources(self, argin):
        """ Invokes AssignResources command on Mcccs Master"""
        handler = self.get_command_object("AssignResources")
        handler(argin)
    

    def is_AssignResources_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean
        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

    @command(
        dtype_in='str',
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """ Invokes ReleaseResources command on MccsMasterLeafNode"""
        handler = self.get_command_object("ReleaseResources")
        handler(argin)

    def is_ReleaseResources_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
                 current device state

        :rtype: boolean

        """
        handler = self.get_command_object("ReleaseResources")
        return handler.check_allowed()
    

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        # Create device_data class object
        device_data = DeviceData.get_instance()

        args = (device_data, self.state_model, self.logger)  
        self.register_command_object("AssignResources", AssignResources(*args))
        self.register_command_object("ReleaseResources", ReleaseResources(*args))
        self.register_command_object("On", On(device_data, self.state_model, self.logger))
        self.register_command_object("Off", Off(device_data, self.state_model, self.logger))



# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsMasterLeafNode.main) ENABLED START #
    """
    Runs the MccsMasterLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: An object of CompletedProcess class returned by the subprocess.
    """
    return run((MccsMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsMasterLeafNode.main

if __name__ == '__main__':
    main()
