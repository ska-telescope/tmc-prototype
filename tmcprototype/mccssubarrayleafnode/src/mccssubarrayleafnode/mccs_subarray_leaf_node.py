# -*- coding: utf-8 -*-
#
# This file is part of the MCCSSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

# Tango imports
from tango import DebugIt, AttrWriteType, DeviceProxy, DevFailed
from tango.server import run, attribute, command, device_property, DeviceMeta
from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState
# Additional import
from . import const, release
# PROTECTED REGION ID(MccsSubarrayLeafNode.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additionnal_import

__all__ = ["MccsSubarrayLeafNode", "main"]


class MccsSubarrayLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(MccsSubarrayLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------





    MCCSSubarrayFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/subarray_01"
    )

    # ----------
    # Attributes
    # ----------









    activitymessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )


    mccssubarrayHealthState = attribute(name="mccssubarrayHealthState", label="mccssubarrayHealthState",
        forwarded=True
    )
    mccsSubarrayObsState = attribute(name="mccsSubarrayObsState", label="mccsSubarrayObsState",
        forwarded=True
    )
    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the MCCSSubarrayLeafNode's init_device() method"
        """

        def do(self):
            """
            Initializes the attributes and properties of the MCCSSubarrayLeafNode.

            :return: A tuple containing a return code and a string message indicating status. The message is
            for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs in creating proxy for MCCSSubarray.
            """
            super().do()
            device = self.target
            try:
                # create MCCSSubarray Proxy
                device._mccs_subarray_proxy = DeviceProxy(device.MCCSSubarrayFQDN)
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY_MCCSSA + str(dev_failed)
                self.logger.debug(log_msg)
                return (ResultCode.FAILED, log_msg)
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._read_activity_message = " "
            device._versioninfo = " "
            device.set_status(const.STR_MCCSSALN_INIT_SUCCESS)
            device._mccs_subarray_health_state = HealthState.OK
            self.logger.info(const.STR_MCCSSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_CSPSALN_INIT_SUCCESS)
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.init_device) ENABLED START #
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.init_device
    
    #TODO: Commenting for now to resolve pylint warnings
    # def init_command_objects(self):
    #     """
    #     Initialises the command handlers for commands supported by this
    #     device.
    #     """
    #     super().init_command_objects()
    #     args = (self, self.state_model, self.logger)
        # self.register_command_object("AssignResources", self.AssignResourcesCommand(*args))

    def always_executed_hook(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activitymessage(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.activitymessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.activitymessage_read

    def write_activitymessage(self, value):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.activitymessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.activitymessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResources(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.AssignResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.AssignResources

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def ReleaseResources(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.ReleaseResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.ReleaseResources

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Configure) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Configure

    @command(
    dtype_in=('str',), 
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Scan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Scan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.EndScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def End(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.End) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.End

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Abort) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Abort

    @command(
    )
    @DebugIt()
    def Restart(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Restart) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Restart

    @command(
    )
    @DebugIt()
    def obsReset(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.obsReset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.obsReset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsSubarrayLeafNode.main) ENABLED START #
    return run((MccsSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.main

if __name__ == '__main__':
    main()
