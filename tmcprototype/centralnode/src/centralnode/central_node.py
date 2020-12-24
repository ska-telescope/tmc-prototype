# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
Central Node is a coordinator of the complete M&C system. Central Node implements the standard set
of state and mode attributes defined by the SKA Control Model.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #

# Tango imports
import tango
from tango import DebugIt, AttrWriteType,  DevFailed
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState
from . import const, release, assign_resources_command, release_resources_command, \
    tango_client, tango_server, stow_antennas_command, stand_by_telescope_command, start_up_telescope_command, \
        health_state_aggreegator, check_receptor_reassignment

from centralnode.resource_manager import ResourceManager
from centralnode.input_validator import AssignResourceValidator
from centralnode.exceptions import ResourceReassignmentError, ResourceNotPresentError
from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError
from centralnode.device_data import DeviceData
from centralnode.obs_state_check import ObsStateAggregator
# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = ["CentralNode", "main", "assign_resources_command","check_receptor_reassignment", "const", "device_data",
           "exceptions", "health_state_aggreegator", "input_validator", "release", "release_resources_command",
           "stand_by_telescope_command", "start_up_telescope_command", "stow_antennas_command", "tango_client",
           "tango_server", "ObsStateAggregator", "resource_manager"]


class CentralNode(SKABaseDevice):
    """
    Central Node is a coordinator of the complete M&C system.
    """

    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #
   
    # obs_state_cb and health_state_cb moved into separate classes.

    # PROTECTED REGION END #    //  CentralNode.class_variable

    # -----------------
    # Device Properties
    # -----------------
    CentralAlarmHandler = device_property(
        dtype='str',
        doc="Device name of CentralAlarmHandler ",
    )

    TMAlarmHandler = device_property(
        dtype='str',
        doc="Device name of TMAlarmHandler ",
    )

    TMMidSubarrayNodes = device_property(
        dtype=('str',), doc="List of TM Mid Subarray Node devices",
        default_value=tuple()
    )

    NumDishes = device_property(
        dtype='uint', default_value=1,
        doc="Number of Dishes",
    )

    DishLeafNodePrefix = device_property(
        dtype='str', default_value='', doc="Device name prefix for Dish Leaf Node"
    )

    CspMasterLeafNodeFQDN = device_property(
        dtype='str'
    )

    SdpMasterLeafNodeFQDN = device_property(
        dtype='str'
    )

    # ----------
    # Attributes
    # ----------

    telescopeHealthState = attribute(
        dtype=HealthState,
        doc="Health state of Telescope",
    )

    subarray1HealthState = attribute(
        dtype=HealthState,
        doc="Health state of Subarray1",
    )

    subarray2HealthState = attribute(
        dtype=HealthState,
        doc="Health state of Subarray2",
    )
    subarray3HealthState = attribute(
        dtype=HealthState,
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    # ---------------
    # General methods
    # ---------------
    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC CentralNode's init_device() method.
        """
        def do(self):
            """
            Initializes the attributes and properties of the Central Node.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs while initializing the CentralNode device or if error occurs while
                    creating device proxy for any of the devices like SubarrayNode, DishLeafNode, CSPMasterLeafNode
                    or SDPMasterLeafNode.

            """
            super().do()

            device = self.target
            try:
                self.logger.info("Device initialisating...")
                # Initialise Attributes
                device._health_state = HealthState.OK
                device._telescope_health_state = HealthState.OK
                device._build_state = '{},{},{}'.format(release.name,release.version,release.description)
                device._version_id = release.version
                device_data = DeviceData.get_instance()
                device_data.csp_master_ln_fqdn = device.CspMasterLeafNodeFQDN
                device_data.sdp_master_ln_fqdn = device.SdpMasterLeafNodeFQDN
                device_data.tm_mid_subarray = device.TMMidSubarrayNodes
                device_data.dln_prefix = device.DishLeafNodePrefix
                device_data.num_dishes = device.NumDishes
                self.logger.debug(const.STR_INIT_SUCCESS)
                device_data.resource_manager_obj = ResourceManager()

                # Initialization of ObsState aggregator object
                device_data.obs_state_aggregator = ObsStateAggregator(
                    device_data.tm_mid_subarray,
                    self.logger)

            except DevFailed as dev_failed:
                log_msg = const.ERR_INIT_PROP_ATTR_CN + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_INIT_PROP_ATTR_CN
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand.do()",
                                             tango.ErrSeverity.ERR)

                #  Get Dish Leaf Node devices List
                # TODO: Getting DishLeafNode devices list from TANGO DB
                # device.tango_db = PyTango.Database()
                # try:
                #     device.dev_dbdatum = device.tango_db.get_device_exported(const.GET_DEVICE_LIST_TANGO_DB)
                #     device._dish_leaf_node_devices.extend(device.dev_bdatum.value_string)
                #     print device._dish_leaf_node_devices

            device_data.resource_manager_obj.init_resource_matrix()
            # Creating proxies for lower level devices

            # Create proxies of Dish Leaf Node devices - this is not required
            # for name in range(0, len(device_data._dish_leaf_node_devices)):
            #     try:
            #         device._leaf_device_proxy.append(DeviceProxy(device_data._dish_leaf_node_devices[name]))
            #     except (DevFailed, KeyError) as except_occurred:
            #         log_msg = const.ERR_IN_CREATE_PROXY + str(except_occurred)
            #         self.logger.exception(except_occurred)
            #         device._read_activity_message = const.ERR_IN_CREATE_PROXY
            #         tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
            #                                      tango.ErrSeverity.ERR)
            #   # REMOVE below code when moved to other class
            # Create device proxy for CSP Master Leaf Node
            # try:
            #     device._csp_master_leaf_proxy = DeviceProxy(device.CspMasterLeafNodeFQDN)
            #     device._csp_master_leaf_proxy.subscribe_event(const.EVT_SUBSR_CSP_MASTER_HEALTH,
            #                                                EventType.CHANGE_EVENT,
            #                                                device.health_state_cb, stateless=True)
            # except DevFailed as dev_failed:
            #     log_msg = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(dev_failed)
            #     self.logger.exception(dev_failed)
            #     device._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
            #     tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
            #                                  tango.ErrSeverity.ERR)
            # # Create device proxy for SDP Master Leaf Node
            # try:
            #     device._sdp_master_leaf_proxy = DeviceProxy(device.SdpMasterLeafNodeFQDN)
            #     device._sdp_master_leaf_proxy.subscribe_event(const.EVT_SUBSR_SDP_MASTER_HEALTH,
            #                                                EventType.CHANGE_EVENT,
            #                                                device.health_state_cb, stateless=True)
            # except DevFailed as dev_failed:
            #     log_msg = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH + str(dev_failed)
            #     self.logger.exception(dev_failed)
            #     device._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH
            #     tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
            #                                  tango.ErrSeverity.ERR)

            # Create device proxy for Subarray Node
            for subarray in range(0, len(device.TMMidSubarrayNodes)):
                try:
                  
                    # REMOVE below code when moved to other class
                    # subarray_proxy = DeviceProxy(device.TMMidSubarrayNodes[subarray])
                    # device.subarray_health_state_map[subarray_proxy] = -1
                    # subarray_proxy.subscribe_event(const.EVT_SUBSR_HEALTH_STATE,
                    #                               EventType.CHANGE_EVENT,
                    #                               device.health_state_cb, stateless=True)

                    # subarray_proxy.subscribe_event(const.EVT_SUBSR_OBS_STATE,
                    #                                EventType.CHANGE_EVENT,
                    #                                device.obs_state_cb, stateless=True)

                    # populate subarrayID-subarray proxy map
                    tokens = device.TMMidSubarrayNodes[subarray].split('/')
                    subarrayID = int(tokens[2])
                    # the below line appends the FQDN of each subarray into the dict
                    device_data.subarray_FQDN_dict[subarrayID] = device.TMMidSubarrayNodes[subarray]
                except DevFailed as dev_failed:
                    log_msg = const.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                    self.logger.exception(dev_failed)
                    device._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                    tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
                                                 tango.ErrSeverity.ERR)

            device_data._read_activity_message = "Central Node initialised successfully."
            self.logger.info(device_data._read_activity_message)
            return (ResultCode.OK, device_data._read_activity_message)


    def always_executed_hook(self):
        # PROTECTED REGION ID(CentralNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CentralNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CentralNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CentralNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_telescopeHealthState(self):
        # PROTECTED REGION ID(CentralNode.telescope_healthstate_read) ENABLED START #
        """ Internal construct of TANGO. Returns the Telescope health state."""
        return self._telescope_health_state
        # PROTECTED REGION END #    //  CentralNode.telescope_healthstate_read

    def read_subarray1HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray1_healthstate_read) ENABLED START #
        """ Internal construct of TANGO. Returns Subarray1 health state. """
        return self._subarray1_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray1_healthstate_read

    def read_subarray2HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray2_healthstate_read) ENABLED START #
        """ Internal construct of TANGO. Returns Subarray2 health state. """
        return self._subarray2_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray2_healthstate_read

    def read_subarray3HealthState(self):
        # PROTECTED REGION ID(CentralNode.subarray3HealthState_read) ENABLED START #
        """ Internal construct of TANGO. Returns Subarray3 health state. """
        return self._subarray3_health_state
        # PROTECTED REGION END #    //  CentralNode.subarray3HealthState_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CentralNode.activity_message_read) ENABLED START #
        """Internal construct of TANGO. Returns activity message. """
        return self._read_activity_message
        # PROTECTED REGION END #    //  CentralNode.activity_message_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CentralNode.activity_message_write) ENABLED START #
        """Internal construct of TANGO. Sets the activity message. """
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CentralNode.activity_message_write

    # --------
    # Commands
    # --------

    # pylint: disable=unused-variable
   
    # pylint: enable=unused-variable

    def is_StowAntennas_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("StowAntennas")
        return handler.check_allowed()

    @command(
        dtype_in=('str',),
        doc_in="List of Receptors to be stowed",
    )
    def StowAntennas(self, argin):
        """
        This command stows the specified receptors.
        """
        handler = self.get_command_object("StowAntennas")
        handler(argin)

    def is_StandByTelescope_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("StandByTelescope")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StandByTelescope(self):
        """
        This command invokes SetStandbyLPMode() command on DishLeafNode, StandBy() command on CspMasterLeafNode and
        SdpMasterLeafNode and Off() command on SubarrayNode and sets CentralNode into OFF state.

        """
        handler = self.get_command_object("StandByTelescope")
        (result_code, message) = handler()
        return [[result_code], [message]]


    def is_StartUpTelescope_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("StartUpTelescope")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def StartUpTelescope(self):
        """
        This command invokes SetOperateMode() command on DishLeadNode, On() command on CspMasterLeafNode,
        SdpMasterLeafNode and SubarrayNode and sets the Central Node into ON state.
        """
        handler = self.get_command_object("StartUpTelescope")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_AssignResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.
    
        :return: True if this command is allowed to be run in current device state
    
        :rtype: boolean
    
        :raises: DevFailed if this command is not allowed to be run in current device state
    
        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()
    
    @command(
        dtype_in='str',
        doc_in="The string in JSON format. The JSON contains following values:\nsubarrayID: "
               "DevShort\ndish: JSON object consisting\n- receptorIDList: DevVarStringArray. "
               "The individual string should contain dish numbers in string format with "
               "preceding zeroes upto 3 digits. E.g. 0001, 0002",
        dtype_out='str',
        doc_out="information-only string",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        AssignResources command invokes the AssignResources command on lower level devices.
        """
        handler = self.get_command_object("AssignResources")
        message = handler(argin)
        return message

    def is_ReleaseResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.
    
        :return: True if this command is allowed to be run in current device state.
    
        :rtype: boolean
    
        :raises: DevFailed if this command is not allowed to be run in current device state
    
        """
        handler = self.get_command_object("ReleaseResources")
        return handler.check_allowed()
    
    @command(
        dtype_in="str",
        doc_in="The string in JSON format. The JSON contains following values:\nsubarrayID: "
               "releaseALL boolean as true and receptorIDList.",
        dtype_out="str",
        doc_out="information-only string",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Release all the resources assigned to the given Subarray.
        """
        handler = self.get_command_object("ReleaseResources")
    
        message = handler(argin)
        return message

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()

        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)
        self.startup_object = start_up_telescope_command.StartUpTelescope(*args)
        self.standby_object = stand_by_telescope_command.StandByTelescope(*args)
        self.assign_object  = assign_resources_command.AssignResources(*args)
        self.release_object = release_resources_command.ReleaseResources(*args)
        self.stow_object = stow_antennas_command.StowAntennas(*args)
        self.register_command_object("AssignResources", self.assign_object)
        self.register_command_object("StowAntennas", self.stow_object)
        self.register_command_object("StartUpTelescope", self.startup_object)
        self.register_command_object("StandByTelescope", self.standby_object)
        self.register_command_object("ReleaseResources", self.release_object)

# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(CentralNode.main) ENABLED START #
    """
    Runs the CentralNode.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: CentralNode TANGO object.
    """
    return run((CentralNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CentralNode.main


if __name__ == '__main__':
    main()
