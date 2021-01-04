"""
CSP Master Leaf node monitors the CSP Master and issues control actions during an observation.
"""

# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(CspMasterLeafNode.import) ENABLED START #
# Third party imports
# PyTango imports
import tango
from tango import ApiUtil, DebugIt, AttrWriteType
from tango.server import run, command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, SimulationMode, TestMode
from . import const, release
from .on_command import On
from .off_command import Off
from .standby_command import Standby
from .device_data import DeviceData

# PROTECTED REGION END #    //  CspMasterLeafNode imports

__all__ = ["CspMasterLeafNode", "main", "On", "Off", "Standby"]


class CspMasterLeafNode(SKABaseDevice):
    """
    **Properties:**

    - CspMasterFQDN   - Property to provide FQDN of CSP Master Device

    # **Attributes:**

    # - cspHealthState  - Forwarded attribute to provide CSP Master Health State
    # - activityMessage - Attribute to provide activity message

    # """


    # -----------------
    # Device Properties
    # -----------------
    CspMasterFQDN = device_property(
        dtype='str'
    )

    # ----------
    # Attributes
    # ----------

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    cspHealthState = attribute(name="cspHealthState", label="cspHealthState", forwarded=True)

    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC CSP Master Leaf Node's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the CspMasterLeafNode.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while creating the device proxy for CSP Master or
                    subscribing the evennts.
            """
            super().do()
            device = self.target
            device_data = DeviceData.get_instance()
            device.device_data = device_data
            device._health_state = HealthState.OK  # Setting healthState to "OK"
            device._simulation_mode = SimulationMode.FALSE  # Enabling the simulation mode
            device._test_mode = TestMode.NONE
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device_data._read_activity_message = const.STR_CSP_INIT_LEAF_NODE
            device_data.csp_master_ln_fqdn = device.CspMasterFQDN

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = const.STR_SETTING_CB_MODEL + str(ApiUtil.instance().get_asynch_cb_sub_model())
            self.logger.debug(log_msg)

            device_data._read_activity_message = const.STR_INIT_SUCCESS
            self.logger.info(device_data._read_activity_message)
            return (ResultCode.OK, device_data._read_activity_message)

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspMasterLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspMasterLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_read) ENABLED START #
        """ Internal construct of TANGO. Returns the activityMessage. """
        return self.device_data._read_activity_message
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_write) ENABLED START #
        """Internal construct of TANGO. Sets the activityMessage. """
        self.device_data._read_activity_message = value
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_write


    def is_Standby_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Standby")
        return handler.check_allowed()

    @command(
        dtype_in=('str',),
        doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
               "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to put in "
               "STANDBY mode.",
    )
    @DebugIt()
    def Standby(self, argin):
        """ Sets Standby Mode on the CSP Element. """
        handler = self.get_command_object("Standby")
        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        device_data = DeviceData.get_instance()
        super().init_command_objects()
        args = (device_data, self.state_model,self.logger)
        self.register_command_object("Off", Off(*args))
        self.register_command_object("On", On(*args))
        self.register_command_object("Standby", Standby(*args))


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspMasterLeafNode.main) ENABLED START #
    """
    Runs the CspMasterLeafNode.

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: CspMasterLeafNode TANGO object.
    
    """
    return run((CspMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspMasterLeafNode.main


if __name__ == '__main__':
    main()
