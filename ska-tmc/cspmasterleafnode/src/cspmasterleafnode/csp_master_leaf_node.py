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
# Tango imports
import os
import tango
from tango import ApiUtil, DebugIt, AttrWriteType
from tango.server import run, command, device_property, attribute
# from tango.server import server_run
# from tango_simlib.tango_sim_generator import (configure_device_models, get_tango_device_server)

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_server_helper import TangoServerHelper
from tmc.common.tango_client import TangoClient

from . import const
from .telescope_on_command import TelescopeOn
from .telescope_off_command import TelescopeOff
from .telescope_standby_command import TelescopeStandby
from .device_data import DeviceData
from .cspmastersimulator import get_csp_master_sim

# PROTECTED REGION END #    //  CspMasterLeafNode imports

__all__ = ["CspMasterLeafNode", "main", "TelescopeOn", "TelescopeOff", "TelescopeStandby"]


class CspMasterLeafNode(SKABaseDevice):
    """
    The primary responsibility of the CSP Master Leaf node is to monitor the CSP Master and issue control
    actions during an observation.

    :Device Properties:

        CspMasterFQDN:
            Property to provide FQDN of CSP Master Device

    :Device Attributes:

        activityMessage:
            Attribute to provide activity message

    """
    # -----------------
    # Device Properties
    # -----------------
    CspMasterFQDN = device_property(dtype="str")

    # ----------
    # Attributes
    # ----------

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
            device.attr_map = {}

            this_device = TangoServerHelper.get_instance()
            this_device.set_tango_class(device)
            this_device.write_attr("activityMessage", const.STR_CSP_INIT_LEAF_NODE, False)

            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            log_msg = f"{const.STR_SETTING_CB_MODEL}{ApiUtil.instance().get_asynch_cb_sub_model()}"
            self.logger.debug(log_msg)

            this_device.write_attr("activityMessage", const.STR_INIT_SUCCESS, False)
            self.logger.info(const.STR_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_INIT_SUCCESS)

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
        return self.attr_map["activityMessage"]
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_write) ENABLED START #
        """Internal construct of TANGO. Sets the activityMessage. """
        self.attr_map["activityMessage"] = value
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_write

    def is_TelescopeOn_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("TelescopeOn")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeOn(self):
        """ Sets On Mode on the CSP Element. """
        handler = self.get_command_object("TelescopeOn")
        handler()


    def is_telescope_off_allowed(self):
        """
        Checks Whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises: DevF
            ailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("TelescopeOff")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def TelescopeOff(self):
        """
        Sets the opState to Off.

        :param argin: None

        :return: None

        """
        handler = self.get_command_object("TelescopeOff")
        handler()


    def is_TelescopeStandby_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("TelescopeStandby")
        return handler.check_allowed()

    @command(
        dtype_in=("str",),
        doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
        "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to put in "
        "STANDBY mode.",
    )
    @DebugIt()
    def TelescopeStandby(self, argin):
        """ Sets Standby Mode on the CSP Element. """
        handler = self.get_command_object("TelescopeStandby")
        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        device_data = DeviceData.get_instance()
        super().init_command_objects()
        args = (device_data, self.state_model, self.logger)
        self.register_command_object("TelescopeOff", TelescopeOff(*args))
        self.register_command_object("TelescopeOn", TelescopeOn(*args))
        self.register_command_object("TelescopeStandby", TelescopeStandby(*args))


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
    #return run((CspMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspMasterLeafNode.main
    
    # Check if standalone mode is enabled
    standalone_mode = os.environ['STANDALONE_MODE']  

    if standalone_mode == "TRUE":
        print("Running in standalone mode")
        device_name = "mid_csp/elt/master"
        csp_master_simulator = get_csp_master_sim(device_name)
        ret_val = run((CspMasterLeafNode,csp_master_simulator), args=args, **kwargs)
    else:
        print("Running in normal mode")
        ret_val = run((CspMasterLeafNode,), args=args, **kwargs)

    return ret_val

if __name__ == "__main__":
    main()
