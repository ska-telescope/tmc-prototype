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
# Third party imports
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, Group
from tango.server import run,attribute, command, device_property

# Additional imports
from . import const, release, assign_resources_command, release_all_resources_command, configure_command,\
    scan_command, end_scan_command, end_command, on_command, off_command, track_command,\
    abort_command, restart_command, obsreset_command, tango_client, tango_server_helper, tango_group_client,\
    health_state_agrregator, obs_state_aggregator
from .const import PointingState
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, ObsMode, ObsState
from ska.base import SKASubarray
from subarraynode.device_data import DeviceData
from subarraynode.tango_client import TangoClient
from subarraynode.tango_server import TangoServer
from subarraynode.exceptions import InvalidObsStateError

__all__ = ["SubarrayNode", "main", "assign_resources_command", "release_all_resources_command",
           "configure_command", "scan_command", "end_scan_command", "end_command", "on_command",
           "off_command", "track_command", "abort_command", "restart_command", "obsreset_command",
           "device_data", "tango_client", "health_state_agrregator", "obs_state_aggregator",
           "tango_group_client", "tango_server_helper"]


class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    # PROTECTED REGION ID(SubarrayNode.class_variable) ENABLED START 

    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(const.PROP_DEF_VAL_LEAF_NODE_PREFIX):
                _ = self.subarray_ln_health_state_map.pop(dev_name)

    # TODO for unsubscribing health and obsState events on CSP and SDP
    def _unsubscribe_csp_sdp_state_events(self, proxy_event_id_map):
        """
        This function unsubscribes all events given by the event ids and their
        corresponding DeviceProxy objects.

        :param 
            device_proxy: Device Proxy
            proxy_event_id: <event_id>

        :return: None

        """
        for device_proxy, event_id in proxy_event_id_map.items():
            try:
                device_proxy.unsubscribe_event(event_id)
            except DevFailed as dev_failed:
                log_message = "Failed to unsubscribe health state event {}.".format(dev_failed)
                self.logger.error(log_message )
                self._read_activity_message = log_message

    def _unsubscribe_resource_events(self, proxy_event_id_map):
        """
        This function unsubscribes all events given by the event ids and their
        corresponding DeviceProxy objects.

        :param proxy_event_id_map: dict
            A mapping of '<DeviceProxy>': <event_id>.

        :return: None

        """
        for device_proxy, event_id in proxy_event_id_map.items():
            try:
                device_proxy.unsubscribe_event(event_id)
            except DevFailed as dev_failed:
                log_message = "Failed to unsubscribe event {}.".format(dev_failed)
                self.logger.error(log_message )
                self._read_activity_message = log_message

    def __len__(self):
        """
        Returns the number of resources currently assigned. Note that
        this also functions as a boolean method for whether there are
        any assigned resources: ``if len()``.

        :return: number of resources assigned
        :rtype: int
        """

        return len(self._receptor_id_list)

    
    def remove_receptors_from_group(self):
        """
        Deletes tango group of the resources allocated in the subarray.

        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVoid
        :return:
            DevVoid
        """
        if not self._dishLnVsHealthEventID or not self._dishLnVsPointingStateEventID:
            return
        try:
            self._dish_leaf_node_group.remove_all()
            log_message = const.STR_GRP_DEF + str(self._dish_leaf_node_group.get_device_list(True))
            self.logger.debug(log_message)
            self._read_activity_message = log_message
            self.logger.info(const.RECEPTORS_REMOVE_SUCCESS)
        except DevFailed as dev_failed:
            log_message = "Failed to remove receptors from the group. {}".format(dev_failed)
            self.logger.error(log_message)
            self._read_activity_message = log_message
            return

        self._unsubscribe_resource_events(self._dishLnVsHealthEventID)
        self._unsubscribe_resource_events(self._dishLnVsPointingStateEventID)

        # clearing dictonaries and lists
        self._dishLnVsHealthEventID.clear()  # Clear eventID dictionary
        self._dishLnVsPointingStateEventID.clear()  # Clear eventID dictionary
        self._health_event_id.clear()
        self._remove_subarray_dish_lns_health_states()
        self.dishPointingStateMap.clear()
        self._pointing_state_event_id.clear()
        self._dish_leaf_node_proxy.clear()
        self._receptor_id_list.clear()
        self.logger.info(const.STR_RECEPTORS_REMOVE_SUCCESS)

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

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the error while subscribing the tango attribute
            """
            super().do()
            device = self.target
            # TODO: get Tangoserver instance
            this_server = TangoServer.get_instance()
            this_server.device = device

            device.set_status(const.STR_SA_INIT)
            device._obs_mode = ObsMode.IDLE
            device.isScanRunning = False
            device.is_end_command = False
            device._scan_id = ""
            device._sb_id = ""
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device.scan_duration = 0
            device._receptor_id_list = []
            device.dishPointingStateMap = {}
            device._dish_leaf_node_proxy = []
            device._health_event_id = []
            device._pointing_state_event_id = []
            device._dishLnVsHealthEventID = {}
            device._dishLnVsPointingStateEventID = {}
            device.only_dishconfig_flag = False
            device.scan_thread = None
            device._read_activity_message = const.STR_SA_INIT_SUCCESS
            # Step 1: Create object of configuration model
            device.device_data = DeviceData.get_instance()
            device.device_data.sdp_subarray_ln_fqdn = device.SdpSubarrayLNFQDN
            device.device_data.csp_subarray_ln_fqdn = device.CspSubarrayLNFQDN
            device.device_data.csp_sa_fqdn = device.CspSubarrayFQDN
            device.device_data.sdp_sa_fqdn = device.SdpSubarrayFQDN
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

    def read_sbID(self):
        """ Internal construct of TANGO. Returns the scheduling block ID. """
        # PROTECTED REGION ID(SubarrayNode.sbID_read) ENABLED START #
        return self._sb_id
        # PROTECTED REGION END #    //  SubarrayNode.sbID_read

    def read_activityMessage(self):
        """ Internal construct of TANGO. Returns activityMessage.
        Example: "Subarray node is initialized successfully"
        //result occured after initialization of device.
        """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        # return self._read_activity_message
        return self.device_data._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        # self._read_activity_message = value
        self.device_data._read_activity_message = value
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

    def is_Track_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

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
        self.configure_obj = configure_command.ConfigureCommand(*args)
        self.assign_obj = assign_resources_command.AssignResourcesCommand(*args)
        self.release_obj = release_all_resources_command.ReleaseAllResourcesCommand(*args)
        self.scan_obj = scan_command.ScanCommand(*args)
        self.endscan_obj = end_scan_command.EndScanCommand(*args)
        self.end_obj = end_command.EndCommand(*args)
        self.restart_obj = restart_command.RestartCommand(*args)
        self.abort_obj = abort_command.AbortCommand(*args)
        self.init_obj = self.InitCommand(*args)
        self.on_obj = on_command.OnCommand(*args)
        self.off_obj = off_command.OffCommand(*args)
        self.obsreset_obj = obsreset_command.ObsResetCommand(*args)

        self.register_command_object("Track", track_command.TrackCommand(*args))
        # In order to pass self = subarray node as target device, the assign and release resource commands
        # are registered and inherited from SKASubarray
        self.register_command_object("AssignResources", self.assign_obj)
        self.register_command_object("ReleaseAllResources", self.release_obj)
        self.register_command_object("Configure", self.configure_obj)
        self.register_command_object("Scan", self.scan_obj)
        self.register_command_object("EndScan", self.endscan_obj)
        self.register_command_object("End", self.end_obj)
        self.register_command_object("On", self.on_obj)
        self.register_command_object("Off", self.off_obj)
        self.register_command_object("Abort", self.abort_obj)
        self.register_command_object("Restart", self.restart_obj)
        self.register_command_object("ObsReset", self.obsreset_obj)

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
