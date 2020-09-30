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
from __future__ import print_function
from __future__ import absolute_import

# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, attribute, command, device_property
from ska.base import SKABaseDevice
from ska.base.commands import ResponseCommand, ResultCode, BaseCommand
from ska.base.control_model import HealthState, ObsState
# Additional import
from . import const, release
from centralnodelow.input_validator import AssignResourceValidator
from centralnodelow.exceptions import ResourceReassignmentError, ResourceNotPresentError
from centralnodelow.exceptions import SubarrayNotPresentError, InvalidJSONError

import json
import ast

# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = ["CentralNode", "main"]


class CentralNode(SKABaseDevice):
    """
    Central Node is a coordinator of the complete M&C system.
    """

    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #
    def health_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray health state and MCCS Master Leaf Node health state, 
        aggregates them to calculate the telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState and MCCSMasterLeafNode healthstate.

        :return: None

        :raises: KeyError if error occurs while setting telescope healthState
        """
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                self.logger.info("healthstate for device:" + str(evt.attr_name))
                self.logger.info("healthstate:" + str(health_state))
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    self._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif self.MCCSMasterLeafNodeFQDN in evt.attr_name:
                    self._mccs_master_leaf_health = health_state
                else:
                    self.logger.debug(const.EVT_UNKNOWN)

                counts = {
                    HealthState.OK: 0,
                    HealthState.DEGRADED: 0,
                    HealthState.FAILED: 0,
                    HealthState.UNKNOWN: 0
                }

                for subsystem_health_field_name in ['mccs_master_leaf_health']:
                    health_state = getattr(self, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1

                for subarray_health_state in list(self.subarray_health_state_map.values()):
                    counts[subarray_health_state] += 1
                
                # Calculating health_state for SubarrayNode, MCCSMasterLeafNode
                if counts[HealthState.OK] == len(list(self.subarray_health_state_map.values())) + 1:
                    self._telescope_health_state = HealthState.OK
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_OK
                elif counts[HealthState.FAILED] != 0:
                    self._telescope_health_state = HealthState.FAILED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_FAILED
                elif counts[HealthState.DEGRADED] != 0:
                    self._telescope_health_state = HealthState.DEGRADED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_DEGRADED
                else:
                    self._telescope_health_state = HealthState.UNKNOWN
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_UNKNOWN
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_UNKNOWN
            else:
                self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            self._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)

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

    TMLowSubarrayNodes = device_property(
        dtype=('str',), doc="List of TM Low Subarray Node devices",
        default_value=tuple()
    )

    MCCSMasterLeafNodeFQDN = device_property(
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
            Initializes the attributes and properties of the Central Node Low.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs while initializing the CentralNode device or if error occurs while
                    creating device proxy for any of the devices like SubarrayNodeLow or MccsMasterLeafNode.

            """
            super().do()

            device = self.target
            try:
                self.logger.info("Device initialisating...")
                device._subarray1_health_state = HealthState.OK
                device._mccs_master_leaf_health = HealthState.OK
                # Initialise Attributes
                device._health_state = HealthState.OK
                device._telescope_health_state = HealthState.OK
                device.subarray_health_state_map = {}
                device.subarray_FQDN_dict = {}
                device._read_activity_message = ""
                device._build_state = '{},{},{}'.format(release.name,release.version,release.description)
                device._version_id = release.version
                self.logger.debug(const.STR_INIT_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_INIT_PROP_ATTR_CN + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_INIT_PROP_ATTR_CN
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand.do()",
                                             tango.ErrSeverity.ERR)

            # Create device proxy for MCCS Master Leaf Node
            try:
                device._mccs_master_leaf_proxy = DeviceProxy(device.MCCSMasterLeafNodeFQDN)
                device._mccs_master_leaf_proxy.subscribe_event(const.EVT_SUBSR_MCCS_MASTER_HEALTH,
                                                           EventType.CHANGE_EVENT,
                                                           device.health_state_cb, stateless=True)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
                                             tango.ErrSeverity.ERR)

            # Create device proxy for Subarray Node
            for subarray in range(0, len(device.TMLowSubarrayNodes)):
                try:
                    subarray_proxy = DeviceProxy(device.TMLowSubarrayNodes[subarray])
                    device.subarray_health_state_map[subarray_proxy] = -1
                    subarray_proxy.subscribe_event(const.EVT_SUBSR_HEALTH_STATE,
                                                  EventType.CHANGE_EVENT,
                                                  device.health_state_cb, stateless=True)

                    # populate subarrayID-subarray proxy map
                    tokens = device.TMLowSubarrayNodes[subarray].split('/')
                    subarrayID = int(tokens[2])
                    device.subarray_FQDN_dict[subarrayID] = subarray_proxy
                except DevFailed as dev_failed:
                    log_msg = const.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                    self.logger.exception(dev_failed)
                    device._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                    tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.InitCommand",
                                                 tango.ErrSeverity.ERR)

            device._read_activity_message = "Central Node initialised successfully."
            self.logger.info(device._read_activity_message)
            return (ResultCode.OK, device._read_activity_message)


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
    
    class StandByTelescopeCommand(SKABaseDevice.OffCommand):
        """
        A class for CentralNode's StandByTelescope() command.
        """

        def check_allowed(self):

            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state
            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command StandByTelescope is not allowed in current state.",
                                             "Failed to invoke StandByTelescope command on CentralNode.",
                                             "CentralNode.StandByTelescope()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self):
            """
            Sets the CentralNode into OFF state. Invokes the respective command on lower level nodes adn devices.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode,
                    DishLeafNode, CSPMasterLeafNode or SDpMasterLeafNode

            """
            device = self.target
            log_msg = const.STR_STANDBY_CMD_ISSUED
            self.logger.info(log_msg)
            device._read_activity_message = log_msg
            # Not required for CN-low
            for name in range(0, len(device._dish_leaf_node_devices)):
                try:
                    device._leaf_device_proxy[name].command_inout(const.CMD_SET_STANDBY_MODE)
                    log_msg = const.CMD_SET_STANDBY_MODE + "invoked on" + str(device._leaf_device_proxy[name])
                    self.logger.info(log_msg)
                    device._leaf_device_proxy[name].command_inout(const.CMD_OFF)
                except DevFailed as dev_failed:
                    log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
                    self.logger.exception(dev_failed)
                    device._read_activity_message = const.ERR_EXE_STANDBY_CMD
                    tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                                 "CentralNode.StandByTelescopeCommand",
                                                 tango.ErrSeverity.ERR)
            # Not required for CN-low , replace with mccsmasterleafnode
            try:
                device._csp_master_leaf_proxy.command_inout(const.CMD_OFF)
                device._csp_master_leaf_proxy.command_inout(const.CMD_STANDBY, [])
                self.logger.info(const.STR_CMD_STANDBY_CSP_DEV)
            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_EXE_STANDBY_CMD
                tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                             "CentralNode.StandByTelescopeCommand",
                                             tango.ErrSeverity.ERR)
            # Not required for CN-low
            try:
                device._sdp_master_leaf_proxy.command_inout(const.CMD_OFF)
                device._sdp_master_leaf_proxy.command_inout(const.CMD_STANDBY)
                self.logger.info(const.STR_CMD_STANDBY_SDP_DEV)
            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_EXE_STANDBY_CMD
                tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                             "CentralNode.StandByTelescopeCommand",
                                             tango.ErrSeverity.ERR)
            try:
                for subarrayID in range(1, len(device.TMMidSubarrayNodes) + 1):
                    device.subarray_FQDN_dict[subarrayID].command_inout(const.CMD_OFF)
                    self.logger.info(const.STR_CMD_STANDBY_SA_DEV)

            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_EXE_STANDBY_CMD
                tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                             "CentralNode.StandByTelescopeCommand",
                                             tango.ErrSeverity.ERR)
            return (ResultCode.OK, device._read_activity_message)

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

    class StartUpTelescopeCommand(SKABaseDevice.OnCommand):
        """
        A class for CentralNode's StartupCommand() command.
        """
        def check_allowed(self):

            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command StartUpTelescope is not allowed in current state.",
                                             "Failed to invoke StartUpTelescope command on CentralNodeLow.",
                                             "CentralNodeLow.StartUpTelescope()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self):
            """
            Setting the startup state to TRUE enables the telescope to accept subarray commands as per the subarray
            model. Set the CentralNode into ON state.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode,
                    DishLeafNode, CSPMasterLeafNode or SDpMasterLeafNode

            """
            device = self.target
            log_msg = const.STR_ON_CMD_ISSUED
            self.logger.info(log_msg)
            device._read_activity_message = log_msg

            try:
                device._mccs_master_leaf_proxy.command_inout(const.CMD_ON)
                self.logger.info(const.STR_CMD_ON_MCCS_DEV)

            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_EXE_ON_CMD
                tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                             "CentralNodeLow.StartUpTelescopeCommand",
                                             tango.ErrSeverity.ERR)

            try:
                for subarrayID in range(1, len(device.TMLowSubarrayNodes) + 1):
                    device.subarray_FQDN_dict[subarrayID].command_inout(const.CMD_ON)
                    self.logger.info(const.STR_CMD_ON_SA_LOW_DEV)
            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device._read_activity_message = const.ERR_EXE_ON_CMD
                tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                             "CentralNodeLow.StartUpTelescopeCommand",
                                             tango.ErrSeverity.ERR)
            return (ResultCode.OK, device._read_activity_message)

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

    class AssignResourcesCommand(BaseCommand):
        """
        A class for CentralNode's AssignResources() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """

            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command AssignResources is not allowed in current state.",
                                             "Failed to invoke AssignResources command on CentralNode.",
                                             "CentralNode.AssignResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self, argin):
            """
            Assigns resources to given subarray. It accepts the subarray id, station ids, station beam id, tile ids list and channels 
            in JSON string format.

            :param argin: The string in JSON format. The JSON contains following values:

               subarray_id:
                   DevShort. Mandatory.
                   the Sub-Array to allocate resources
               station_ids:
                    DevArray. Mandatory
                    list of stations contributing beams to the data set
               channels:
                    DevArray. Mandatory
                    list of frequency channels used
               station_beam_ids:
                    DevArray. Mandatory
                    logical ID of beam
               tile_ids:
                    DevArray. Mandatory
                    the list of tiles that should be allocated to the Sub-Array

            Example:
                {
                    "subarray_id": 1,
                    "station_ids": [1,2],
                    "channels": [1,2,3,4,5,6,7,8],
                    "station_beam_ids": [1],
                    "tile_ids": [1,2,3,4],
                }

            Note: From Jive, enter above input string without any space.

            :return: None

            :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode, MCCSMasterLeafNode

            Note: Enter input without spaces as:{"subarray_id":1,"station_ids":[1,2],"channels":[1,2,3,4,5,6,7,8],"station_beam_ids":[1],"tile_ids":[1,2,3,4],}

            """
            device = self.target
            try:
                json_argument = json.loads(argin)
                # Create subarray proxy
                subarray_id = int(json_argument['subarray_id'])
                subarrayProxy = device.subarray_FQDN_dict[subarray_id]
                
                # Allocate resources to subarray
                self.logger.info("Allocating resource to subarray %d", subarray_id)
                input_to_sa = json.dumps(json_argument)
                # TODO: Need to think if anything will be returned from SubarrayNode
                subarrayProxy.command_inout(const.CMD_ASSIGN_RESOURCES, input_to_sa)
                # Invoke command on MCCS Master leaf node
                self.logger.info("Invoking AssignResources command on MCCS Master Leaf Node")
                input_to_mccs = json.dumps(json_argument)
                device._mccs_master_leaf_proxy.command_inout(const.CMD_ASSIGN_RESOURCES, input_to_mccs)
                
                # Allocation successful
                device._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
                self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

            except ValueError as val_error:
                self.logger.exception("Exception in AssignResources command: %s", str(val_error))
                device._read_activity_message = "Invalid value in input: " + str(val_error)
                log_msg = const.STR_ASSIGN_RES_EXEC + str(val_error)
                self.logger.exception(val_error)
                tango.Except.throw_exception(const.STR_RESOURCE_ALLOCATION_FAILED, log_msg,
                                             "CentralNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)
            except DevFailed as dev_failed:
                log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                             "CentralNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)
            # PROTECTED REGION END #    //  CentralNode.AssignResources

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
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        AssignResources command invokes the AssignResources command on lower level devices.
        """
        handler = self.get_command_object("AssignResources")
        handler(argin)

    class ReleaseResourcesCommand(BaseCommand):
        """
        A class for CentralNode's ReleaseResources() command.
        """
        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """

            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,]:
                tango.Except.throw_exception("Command ReleaseResources is not allowed in current state.",
                                             "Failed to invoke ReleaseResources command on CentralNode.",
                                             "CentralNode.ReleaseResources()",
                                             tango.ErrSeverity.ERR)
            return True
        
        def do(self, argin):
            """
            Release all the resources assigned to the given Subarray. It accepts the subarray id, releaseALL flag in JSON string format. When the releaseALL flag is True, ReleaseAllResources command
            is invoked on the respective SubarrayNode. 
            
            :param argin: The string in JSON format. The JSON contains following values:

                subarrayID:
                    DevShort. Mandatory.

                releaseALL:
                    Boolean(True or False). Mandatory. True when all the resources to be released from Subarray.

                Example:
                    {
                        "subarrayID": 1,
                        "releaseALL": true,
                    }

                Note: From Jive, enter input as:
                    {"subarrayID":1,"releaseALL":true} without any space.

             :raises: ValueError if input argument json string contains invalid value
                    KeyError if input argument json string contains invalid key
                    DevFailed if the command execution or command invocation on SubarrayNode is not successful

            """
            device = self.target
            try:
                release_success = False
                jsonArgument = json.loads(argin)
                subarrayID = jsonArgument['subarrayID']
                subarrayProxy = device.subarray_FQDN_dict[subarrayID]
                subarray_name = "SA" + str(subarrayID)
                if jsonArgument['releaseALL'] == True:
                    # Invoke "ReleaseAllResources" on SubarrayNode
                    subarrayProxy.command_inout(const.CMD_RELEASE_RESOURCES)
                    device._mccs_master_leaf_proxy.command_inout(const.CMD_RELEASE_RESOURCES)
                    log_msg = const.STR_REL_RESOURCES
                    self.logger.info(log_msg)
                    device._read_activity_message = log_msg
                else:
                    device._read_activity_message = const.STR_FALSE_TAG
                    self.logger.info(const.STR_FALSE_TAG)

            except ValueError as value_error:
                self.logger.error(const.ERR_INVALID_JSON)
                device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
                log_msg = const.ERR_INVALID_JSON + str(value_error)
                self.logger.exception(value_error)
                tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                             "CentralNode.ReleaseResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except KeyError as key_error:
                self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                self.logger.exception(key_error)
                tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                             "CentralNode.ReleaseResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_RELEASE_RESOURCES + str(dev_failed)
                device._read_activity_message = const.ERR_RELEASE_RESOURCES
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                             "CentralNode.ReleaseResourcesCommand",
                                             tango.ErrSeverity.ERR)

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
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Release all the resources assigned to the given Subarray.
        """
        handler = self.get_command_object("ReleaseResources")

        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("StartUpTelescope", self.StartUpTelescopeCommand(*args))
        self.register_command_object("StandByTelescope", self.StandByTelescopeCommand(*args))
        self.register_command_object("AssignResources", self.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseResources", self.ReleaseResourcesCommand(*args))

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
