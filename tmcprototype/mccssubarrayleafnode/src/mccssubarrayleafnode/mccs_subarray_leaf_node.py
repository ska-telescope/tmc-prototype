# -*- coding: utf-8 -*-
#
# This file is part of the MccsSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" 

"""

# Tango imports
from tango import AttrWriteType, DeviceProxy, DevFailed
from tango.server import run, attribute, device_property
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
   
    # PROTECTED REGION ID(MCCSSubarrayLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------

    MccsSubarrayFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/subarray_01"
    )

    # ----------
    # Attributes
    # ----------

    activityMessage = attribute(
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
        A class for the MccsSubarrayLeafNode's init_device() method"
        """

        def do(self):
            """
            Initializes the attributes and properties of the MccsSubarrayLeafNode.

            :return: A tuple containing a return code and a string message indicating status. The message is
            for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs in creating proxy for MCCSSubarray.
            """
            super().do()
            device = self.target
            try:
                # create MccsSubarray Proxy
                device._mccs_subarray_proxy = DeviceProxy(device.MccsSubarrayFQDN)
                self.logger.info("Mccs Subarray device proxy created successfully.")
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY_MCCSSA + str(dev_failed)
                self.logger.debug(log_msg)
                return (ResultCode.FAILED, log_msg)
            #TODO
            # self.set_change_event("adminMode", True, True)
            # self.set_archive_event("adminMode", True, True)
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._read_activity_message = " "
            device._versioninfo = " "
            device.set_status(const.STR_MCCSSALN_INIT_SUCCESS)
            device._mccs_subarray_health_state = HealthState.OK
            self.logger.info(const.STR_MCCSSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_MCCSSALN_INIT_SUCCESS)
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.init_device) ENABLED START #
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.delete_device

    # TODO: Commented out for now to resolve pylint warnings.
    # def init_command_objects(self):
    #     """
    #     Initialises the command handlers for commands supported by this
    #     device.
    #     """
    #     super().init_command_objects()
        # args = (self, self.state_model, self.logger)


    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(MccsSubarrayLeafNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  MccsSubarrayLeafNode.activityMessage_write




    # --------
    # Commands
    # --------

    
    # ----------
    # Run server
    # ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MccsSubarrayLeafNode.main) ENABLED START #
    return run((MccsSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MccsSubarrayLeafNode.main


if __name__ == '__main__':
    main()
