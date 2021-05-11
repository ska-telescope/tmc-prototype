"""
CSP Subarray Leaf node monitors the CSP Subarray and issues control actions during an observation.
It also acts as a CSP contact point for Subarray Node for observation execution for TMC.
"""
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(CspSubarrayLeafNode.additional_import) ENABLED START #
# Standard python imports

import threading

# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, ApiUtil
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from cspsubarrayleafnode.device_data import DeviceData
from .assign_resources_command import AssignResourcesCommand
from .release_all_resources_command import ReleaseAllResourcesCommand
from .configure_command import ConfigureCommand
from .scan_command import StartScanCommand
from .end_scan_command import EndScanCommand
from .end_command import GoToIdleCommand
from .abort_command import AbortCommand
from .restart_command import RestartCommand
from .obsreset_command import ObsResetCommand
from .on_command import On
from .off_command import Off
from . import const, release
from .exceptions import InvalidObsStateError
from .delay_model import DelayManager

# PROTECTED REGION END #    //  CspSubarrayLeafNode.additional_import

__all__ = [
    "CspSubarrayLeafNode",
    "main",
    "AssignResourcesCommand",
    "ReleaseAllResourcesCommand",
    "ConfigureCommand",
    "StartScanCommand",
    "EndScanCommand",
    "GoToIdleCommand",
    "AbortCommand",
    "RestartCommand",
    "ObsResetCommand",
    "On",
    "Off",
]


class CspSubarrayLeafNode(SKABaseDevice):
    """
    CSP Subarray Leaf node monitors the CSP Subarray and issues control actions during an observation.

    :Device Properties:

        CspSubarrayFQDN:
            Property to provide FQDN of CSP Subarray Device

    :Device Attributes:

        cspsubarrayHealthState:
            Forwarded attribute to provide CSP Subarray Health State

        cspSubarrayObsState:
            Forwarded attribute to provide CSP Subarray Observation State

        activityMessage:
            String providing information about the current activity in CspSubarrayLeaf Node.

        delayModel:
            Attribute to provide the delay model.

        versionInfo:
            Provides Version information of TANGO device.

    """

    # -----------------
    # Device Properties
    # -----------------
    CspSubarrayFQDN = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------
    delayModel = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
    )

    versionInfo = attribute(
        dtype="str",
    )

    activityMessage = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
    )

    cspsubarrayHealthState = attribute(
        name="cspsubarrayHealthState", label="cspsubarrayHealthState", forwarded=True
    )

    cspSubarrayObsState = attribute(
        name="cspSubarrayObsState", label="cspSubarrayObsState", forwarded=True
    )

    # ---------------
    # General methods
    # ---------------
    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the CspSubarrayLeafNode's init_device() method"
        """

        def do(self):
            """
            Initializes the attributes and properties of the CspSubarrayLeafNode.

            :return: A tuple containing a return code and a string message indicating status. The message is
            for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs in creating proxy for CSPSubarray.
            """
            super().do()
            device = self.target

            this_server = TangoServerHelper.get_instance()
            this_server.set_tango_class(device)
            device.attr_map = {}
            device.attr_map["delayModel"] = " "
            device.attr_map["activityMessage"] = ""

            device._build_state = "{},{},{}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version
            device._versioninfo = " "
            # The IERS_A file needs to be downloaded each time when the MVP is deployed.
            delay_manager_obj = DelayManager.get_instance() 
            delay_manager_obj.download_IERS_file()
            ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
            this_server.write_attr("activityMessage", f"{const.STR_SETTING_CB_MODEL}{ApiUtil.instance().get_asynch_cb_sub_model()}", False)
            this_server.set_status(const.STR_CSPSALN_INIT_SUCCESS)
            this_server.write_attr("activityMessage", const.STR_CSPSALN_INIT_SUCCESS, False)
            self.logger.info(const.STR_CSPSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_CSPSALN_INIT_SUCCESS)

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        self.logger.debug("Exiting.")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------
    def read_delayModel(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_read) ENABLED START #
        """Internal construct of TANGO. Returns the delay model."""
        return self.attr_map["delayModel"]
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_read

    def write_delayModel(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_write) ENABLED START #
        """Internal construct of TANGO. Sets in to the delay model."""
        self.update_attr_map("delayModel", value)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_write

    def read_versionInfo(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.versionInfo_read) ENABLED START #
        """Internal construct of TANGO. Returns the version information."""
        return self._versioninfo
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_read) ENABLED START #
        """Internal construct of TANGO. Returns activity message."""
        return self.attr_map["activityMessage"]
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_write) ENABLED START #
        """Internal construct of TANGO. Sets the activity message."""
        self.update_attr_map("activityMessage", value)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_write

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

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(
        dtype_in=("str"),
        doc_in="The string in JSON format, contains CSP configuration id, frequencyBand, fsp,"
        " delayModelSubscriptionPoint and pointing information.",
    )
    @DebugIt()
    def Configure(self, argin):
        """ Invokes Configure command on CspSubarrayLeafNode """
        handler = self.get_command_object("Configure")
        handler(argin)

    @command(
        dtype_in=("str",),
        doc_in="The string in JSON format, consists of scan id.",
    )
    @DebugIt()
    def StartScan(self, argin):
        """ Invokes StartScan command on cspsubarrayleafnode"""
        handler = self.get_command_object("StartScan")
        handler(argin)

    def is_StartScan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("StartScan")
        return handler.check_allowed()

    def is_EndScan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def EndScan(self):
        """ Invokes EndScan command on CspSubarrayLeafNode"""
        handler = self.get_command_object("EndScan")
        handler()

    def is_ReleaseAllResources_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("ReleaseAllResources")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def ReleaseAllResources(self):
        """ Invokes ReleaseAllResources command on CspSubarrayLeafNode"""
        handler = self.get_command_object("ReleaseAllResources")
        handler()

    def is_AssignResources_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

    @command(
        dtype_in=("str"),
        doc_in="The input string in JSON format consists of receptorIDList.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """ Invokes AssignResources command on CspSubarrayLeafNode. """
        handler = self.get_command_object("AssignResources")
        try:
            self.validate_obs_state()

        except InvalidObsStateError as error:
            self.logger.exception(error)
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_EMPTY_OR_IDLE,
                                         "CSP subarray leaf node raised exception",
                                         "CSP.AddReceptors",
                                         tango.ErrSeverity.ERR)
        handler(argin)

    def is_GoToIdle_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
        current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        handler = self.get_command_object("GoToIdle")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def GoToIdle(self):
        """ Invokes GoToIdle command on CspSubarrayLeafNode. """
        handler = self.get_command_object("GoToIdle")
        handler()

    def validate_obs_state(self):
        this_server = TangoServerHelper.get_instance()
        csp_subarray_fqdn = this_server.read_property("CspSubarrayFQDN")[0]
        csp_sa_client = TangoClient(csp_subarray_fqdn)
        if csp_sa_client.get_attribute("obsState").value in [ObsState.EMPTY, ObsState.IDLE]:
            self.logger.info(
                "CSP Subarray is in required obsState, resources will be assigned"
            )
        else:
            self.logger.error("CSP Subarray is not in EMPTY/IDLE obsState")
            this_server.write_attr("activityMessage", "Error in device obsState", False)
            raise InvalidObsStateError("CSP Subarray is not in EMPTY/IDLE obsState")

    @command()
    @DebugIt()
    def Abort(self):
        """ Invokes Abort command on CspSubarrayLeafNode"""
        handler = self.get_command_object("Abort")
        handler()

    def is_Abort_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
                 current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
                 in current device state
        """
        handler = self.get_command_object("Abort")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def Restart(self):
        """ Invokes Restart command on cspsubarrayleafnode"""
        handler = self.get_command_object("Restart")
        handler()

    def is_Restart_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
                 current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
                 in current device state
        """
        handler = self.get_command_object("Restart")
        return handler.check_allowed()

    @command()
    @DebugIt()
    def ObsReset(self):
        """ Invokes ObsReset command on cspsubarrayleafnode"""
        handler = self.get_command_object("ObsReset")
        handler()

    def is_ObsReset_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
                 current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
                 in current device state
        """
        handler = self.get_command_object("ObsReset")
        return handler.check_allowed()

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.register_command_object("AssignResources", AssignResourcesCommand(*args))
        self.register_command_object(
            "ReleaseAllResources", ReleaseAllResourcesCommand(*args)
        )
        self.register_command_object("Configure", ConfigureCommand(*args))
        self.register_command_object("StartScan", StartScanCommand(*args))
        self.register_command_object("EndScan", EndScanCommand(*args))
        self.register_command_object("GoToIdle", GoToIdleCommand(*args))
        self.register_command_object("Abort", AbortCommand(*args))
        self.register_command_object("Restart", RestartCommand(*args))
        self.register_command_object("ObsReset", ObsResetCommand(*args))
        self.register_command_object("Off", Off(*args))
        self.register_command_object("On", On(*args))


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspSubarrayLeafNode.main) ENABLED START #
    """
    Runs the CspSubarrayLeafNode.

    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO

    :return: CspSubarrayLeafNode TANGO object.

    """
    return run((CspSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.main


if __name__ == "__main__":
    main()
