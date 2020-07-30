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
from ska.base.commands import ResponseCommand, ResultCode
from ska.base.control_model import HealthState
# Additional import
from . import const
from centralnode.input_validator import AssignResourceValidator
from centralnode.exceptions import ResourceReassignmentError, ResourceNotPresentError
from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError

import json
import ast

# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = ["CentralNode", "main"]


class CentralNode(SKABaseDevice):
    """
    Central Node is a coordinator of the complete M&C system.
    """

    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #
    @DebugIt()
    def _check_receptor_reassignment(self, input_receptors_list):
        """
        Checks if any of the receptors are already allocated to other subarray when AssignResources command is called.

        :param: argin: The input receptor list

        :return: None

        :throws:
            ResourceReassignmentError: Thrown when an already assigned resource is received
            in Assignresources command.

        """

        self.logger.info("Checking for duplicate allocation of dishes.")
        duplicate_allocation_count = 0
        duplicate_allocation_dish_ids = []
        self.logger.info(self._subarray_allocation)

        for receptor in input_receptors_list:
            dish_ID = "dish" + receptor
            self.logger.info("Checking allocation status of dish %s.", dish_ID)
            if self._subarray_allocation[dish_ID] != "NOT_ALLOCATED":
                self.logger.info("Dish %s is already allocated.", dish_ID)
                # duplicate_allocation_dish_ids.append(dish_ID)
                duplicate_allocation_dish_ids.append(receptor)
                duplicate_allocation_count = duplicate_allocation_count + 1
        self.logger.info("No of dishes already allocated: %d", duplicate_allocation_count)
        self.logger.info("List of dishes already allocated: %s", str(duplicate_allocation_dish_ids))

        if duplicate_allocation_count > 0:
            exception_message = "The following Receptor id(s) are allocated to other subarrays: "
            exception_message += (str(duplicate_allocation_dish_ids))
            raise ResourceReassignmentError(exception_message)

    def health_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None

        :raises: KeyError if error occurs while setting Subarray healthState
                Exception if error occurs in aggregating the health state of the telescope
        """
        exception_count = 0
        exception_message = []
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    self._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    self._subarray2_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    self._subarray3_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif self.CspMasterLeafNodeFQDN in evt.attr_name:
                    self._csp_master_leaf_health = health_state
                elif self.SdpMasterLeafNodeFQDN in evt.attr_name:
                    self._sdp_master_leaf_health = health_state
                else:
                    self.logger.debug(const.EVT_UNKNOWN)
                    # TODO: For future reference
                    # self._read_activity_message = const.EVT_UNKNOWN

                counts = {
                    HealthState.OK: 0,
                    HealthState.DEGRADED: 0,
                    HealthState.FAILED: 0,
                    HealthState.UNKNOWN: 0
                }

                for subsystem_health_field_name in ['csp_master_leaf_health', 'sdp_master_leaf_health']:
                    health_state = getattr(self, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1

                for subarray_health_state in list(self.subarray_health_state_map.values()):
                    counts[subarray_health_state] += 1

                # Calculating health_state for SubarrayNode, CspMasterLeafNode, SdpMasterLeafNode
                if counts[HealthState.OK] == len(list(self.subarray_health_state_map.values())) + 2:
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
                # TODO: For future reference
                self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            # TODO: For future reference
            self._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)
        except Exception as except_occured:
            [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                                                  exception_message, exception_count,
                                                                                  const.ERR_AGGR_HEALTH_STATE)

    def _handle_devfailed_exception(self, df, excpt_msg_list, exception_count, read_actvity_msg):
        str_log = read_actvity_msg + str(df)
        self.logger.error(str_log)
        self._read_activity_message = read_actvity_msg + str(df)
        excpt_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [excpt_msg_list, exception_count]

    def _handle_generic_exception(self, exception, excpt_msg_list, exception_count, read_actvity_msg):
        str_log = read_actvity_msg + str(exception)
        self.logger.error(str_log)
        self._read_activity_message = read_actvity_msg + str(exception)
        excpt_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [excpt_msg_list, exception_count]

    def throw_exception(self, excpt_msg_list, read_actvity_msg):
        err_msg = ''
        for item in excpt_msg_list:
            err_msg += item + "\n"
        tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)
        self.logger.error(const.STR_CMD_FAILED)

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

            exception_count = 0
            exception_message = []
            try:
                self.logger.info("Device initialisating...")
                device._subarray1_health_state = HealthState.OK
                device._subarray2_health_state = HealthState.OK
                device._subarray3_health_state = HealthState.OK
                device._sdp_master_leaf_health = HealthState.OK
                device._csp_master_leaf_health = HealthState.OK
                # Initialise Attributes
                device._health_state = HealthState.OK
                device._telescope_health_state = HealthState.OK
                device.subarray_health_state_map = {}
                device._dish_leaf_node_devices = []
                device._leaf_device_proxy = []
                device.subarray_FQDN_dict = {}
                device._subarray_allocation = {}
                device._read_activity_message = ""
                self.logger.debug(const.STR_INIT_SUCCESS)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed, exception_message,
                                                                                        exception_count, const.ERR_INIT_PROP_ATTR_CN)
                device._read_activity_message = const.ERR_INIT_PROP_ATTR_CN

                #  Get Dish Leaf Node devices List
                # TODO: Getting DishLeafNode devices list from TANGO DB
                # device.tango_db = PyTango.Database()
                # try:
                #     device.dev_dbdatum = device.tango_db.get_device_exported(const.GET_DEVICE_LIST_TANGO_DB)
                #     device._dish_leaf_node_devices.extend(device.dev_bdatum.value_string)
                #     print device._dish_leaf_node_devices
                #
                # except Exception as except_occured:
                #     print const.ERR_IN_READ_DISH_LN_DEVS, except_occured
                #     device._read_activity_message = const.ERR_IN_READ_DISH_LN_DEVS + str(except_occured)
                #     self.dev_logging(const.ERR_IN_READ_DISH_LN_DEVS, int(tango.LogLevel.LOG_ERROR))

            # Creating proxies for lower level devices
            for dish in range(1, (device.NumDishes + 1)):
                # Update device._dish_leaf_node_devices variable
                device._dish_leaf_node_devices.append(device.DishLeafNodePrefix + "000" + str(dish))

                # Initialize device.subarray_allocation variable (map of Dish Id and allocation status)
                # to indicate availability of the dishes
                dish_ID = "dish000" + str(dish)
                device._subarray_allocation[dish_ID] = "NOT_ALLOCATED"

            # Create proxies of Dish Leaf Node devices
            for name in range(0, len(device._dish_leaf_node_devices)):
                try:
                    device._leaf_device_proxy.append(DeviceProxy(device._dish_leaf_node_devices[name]))
                except (DevFailed, KeyError) as except_occurred:
                    [exception_message, exception_count] = device._handle_devfailed_exception(except_occurred,
                                                                                           exception_message,
                                                                                           exception_count,
                                                                                           const.ERR_IN_CREATE_PROXY)
                    device._read_activity_message = const.ERR_IN_CREATE_PROXY

            # Create device proxy for CSP Master Leaf Node
            try:
                device._csp_master_leaf_proxy = DeviceProxy(device.CspMasterLeafNodeFQDN)
                device._csp_master_leaf_proxy.subscribe_event(const.EVT_SUBSR_CSP_MASTER_HEALTH,
                                                           EventType.CHANGE_EVENT,
                                                           device.health_state_cb, stateless=True)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                       exception_message,
                                                                                       exception_count,
                                                                                       const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH)
                device._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH

            # Create device proxy for SDP Master Leaf Node
            try:
                device._sdp_master_leaf_proxy = DeviceProxy(device.SdpMasterLeafNodeFQDN)
                device._sdp_master_leaf_proxy.subscribe_event(const.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                           EventType.CHANGE_EVENT,
                                                           device.health_state_cb, stateless=True)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                       exception_message,
                                                                                       exception_count,
                                                                                       const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH)
                device._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH

            # Create device proxy for Subarray Node
            for subarray in range(0, len(device.TMMidSubarrayNodes)):
                try:
                    subarray_proxy = DeviceProxy(device.TMMidSubarrayNodes[subarray])
                    device.subarray_health_state_map[subarray_proxy] = -1
                    subarray_proxy.subscribe_event(const.EVT_SUBSR_HEALTH_STATE,
                                                  EventType.CHANGE_EVENT,
                                                  device.health_state_cb, stateless=True)

                    # populate subarrayID-subarray proxy map
                    tokens = device.TMMidSubarrayNodes[subarray].split('/')
                    subarrayID = int(tokens[2])
                    device.subarray_FQDN_dict[subarrayID] = subarray_proxy
                except DevFailed as dev_failed:
                    [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                           exception_message,
                                                                                           exception_count,
                                                                                           const.ERR_SUBSR_SA_HEALTH_STATE)
                    device._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE

            if exception_count >0:
                self.logger.info(device._read_activity_message)
                device.throw_exception(exception_message, device._read_activity_message)

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

    class StowAntennasCommand(ResponseCommand):
        """
        A class for CentralNode's StowAntennas() command.
        """

        def check_allowed(self):

            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command StowAntennas is not allowed in current state.",
                                             "Failed to invoke StowAntennas command on CentralNode.",
                                             "CentralNode.StowAntennas()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self, argin):
            """
            Invokes the command SetStowMode on the specified receptors.

            :param argin: List of Receptors to be stowed.

            :return: None

            :raises: DevFailed if error occurs while invoking command of DishLeafNode
                    ValueError if error occurs if input argument json string contains invalid value
                    Exception if command execution throws any type of exception

            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                for leafId in range(0, len(argin)):
                    if type(float(argin[leafId])) == float:
                        pass
                log_msg = const.STR_STOW_CMD_ISSUED_CN
                self.logger.info(log_msg)
                device._read_activity_message = log_msg
                for i in range(0, len(argin)):
                    device_name = device.DishLeafNodePrefix + argin[i]
                    try:
                        device_proxy = DeviceProxy(device_name)
                        device_proxy.command_inout(const.CMD_SET_STOW_MODE)
                    except DevFailed as dev_failed:
                        [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                                  exception_message,
                                                                                                  exception_count,
                                                                                                  const.ERR_EXE_STOW_CMD)
                        device._read_activity_message = const.ERR_EXE_STOW_CMD

            except ValueError as value_error:
                self.logger.error(const.ERR_STOW_ARGIN)
                device._read_activity_message = const.ERR_STOW_ARGIN + str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            except Exception as except_occured:
                [exception_message, exception_count] = device._handle_generic_exception(except_occured,
                                                                                        exception_message,
                                                                                        exception_count,
                                                                                        const.ERR_EXE_STOW_CMD)
                device._read_activity_message = const.ERR_EXE_STOW_CMD

            # throw exception:
            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_STOW_ANTENNA_EXEC)

            return (ResultCode.OK, device._read_activity_message)

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
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StowAntennas(self, argin):
        """
        This command stows the specified receptors.
        """
        handler = self.get_command_object("StowAntennas")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

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
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
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
            exception_count = 0
            exception_message = []
            log_msg = const.STR_STANDBY_CMD_ISSUED
            self.logger.info(log_msg)
            device._read_activity_message = log_msg

            for name in range(0, len(device._dish_leaf_node_devices)):
                try:
                    device._leaf_device_proxy[name].command_inout(const.CMD_SET_STANDBY_MODE)
                    log_msg = const.CMD_SET_STANDBY_MODE + "invoked on" + str(device._leaf_device_proxy[name])
                    self.logger.info(log_msg)
                except DevFailed as dev_failed:
                    [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                              exception_message,
                                                                                              exception_count,
                                                                                              const.ERR_EXE_STANDBY_CMD)
                    device._read_activity_message = const.ERR_EXE_STANDBY_CMD

            try:
                device._csp_master_leaf_proxy.command_inout(const.CMD_STANDBY, [])
                self.logger.info(const.STR_CMD_STANDBY_CSP_DEV)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_STANDBY_CMD)
                device._read_activity_message = const.ERR_EXE_STANDBY_CMD

            try:
                device._sdp_master_leaf_proxy.command_inout(const.CMD_STANDBY)
                self.logger.info(const.STR_CMD_STANDBY_SDP_DEV)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_STANDBY_CMD)
                device._read_activity_message = const.ERR_EXE_STANDBY_CMD

            try:
                for subarrayID in range(1, len(device.TMMidSubarrayNodes) + 1):
                    device.subarray_FQDN_dict[subarrayID].command_inout(const.CMD_OFF)
                    self.logger.info(const.STR_CMD_STANDBY_SA_DEV)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_STANDBY_CMD)
                device._read_activity_message = const.ERR_EXE_STANDBY_CMD

            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_STANDBY_EXEC)

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
            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command StartUpTelescope is not allowed in current state.",
                                             "Failed to invoke StartUpTelescope command on CentralNode.",
                                             "CentralNode.StartUpTelescope()",
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
            exception_count = 0
            exception_message = []
            log_msg = const.STR_ON_CMD_ISSUED
            self.logger.info(log_msg)
            device._read_activity_message = log_msg

            for name in range(0, len(device._dish_leaf_node_devices)):
                try:
                    device._leaf_device_proxy[name].command_inout(const.CMD_ON)
                    device._leaf_device_proxy[name].command_inout(const.CMD_SET_OPERATE_MODE)
                    log_msg = const.CMD_SET_OPERATE_MODE + 'invoked on' + str(device._leaf_device_proxy[name])
                    self.logger.info(log_msg)
                except DevFailed as dev_failed:
                    [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed, exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_ON_CMD)

                    device._read_activity_message =  const.ERR_EXE_ON_CMD

            try:
                device._csp_master_leaf_proxy.command_inout(const.CMD_ON)
                self.logger.info(const.STR_CMD_ON_CSP_DEV)

            except Exception as except_occured:
                [exception_message, exception_count] = device._handle_generic_exception(except_occured,exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_ON_CMD)

                device._read_activity_message =  const.ERR_EXE_ON_CMD

            try:
                device._sdp_master_leaf_proxy.command_inout(const.CMD_ON)
                self.logger.info(const.STR_CMD_ON_SDP_DEV)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_ON_CMD)

                device._read_activity_message = const.ERR_EXE_ON_CMD

            try:
                for subarrayID in range(1, len(device.TMMidSubarrayNodes) + 1):
                    device.subarray_FQDN_dict[subarrayID].command_inout(const.CMD_ON)
                    self.logger.info(const.STR_CMD_ON_SA_DEV)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_EXE_ON_CMD)

                device._read_activity_message =  const.ERR_EXE_ON_CMD

            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_ON_EXEC)

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

    class AssignResourcesCommand(ResponseCommand):
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

            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Command AssignResources is not allowed in current state.",
                                             "Failed to invoke AssignResources command on CentralNode.",
                                             "CentralNode.AssignResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self, argin):
            """
            Assigns resources to given subarray. It accepts the subarray id, receptor id list and SDP block in JSON
            string format. Upon successful execution, the 'receptorIDList' attribute of the given subarray is populated
            with the given receptors.Also checking for duplicate allocation of resources is done. If already allocated
            it will throw error message regarding the prior existence of resource.

            :param argin: The string in JSON format. The JSON contains following values:

               subarrayID:
                   DevShort. Mandatory.

               dish:
                   Mandatory JSON object consisting of

                   receptorIDList:
                       DevVarStringArray
                       The individual string should contain dish numbers in string format
                       with preceding zeroes upto 3 digits. E.g. 0001, 0002.

               sdp:
                   Mandatory JSON object consisting of

                   id:
                       DevString
                       The SBI id.
                   max_length:
                       DevDouble
                       Maximum length of the SBI in seconds.
                   scan_types:
                       array of the blocks each consisting following parameters
                       id:
                           DevString
                           The scan id.
                       coordinate_system:
                           DevString
                       ra:
                           DevString
                       Dec:
                           DevString

                   processing_blocks:
                       array of the blocks each consisting following parameters
                       id:
                           DevString
                           The Processing Block id.
                       workflow:
                           type:
                               DevString
                           id:
                               DevString
                           version:
                               DevString
                       parameters:
                           {}

            Example:
                {"subarrayID":1,"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001",
                "max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS","ra":"02:42:40.771"
                ,"dec":"-00:00:47.84","channels":[{"count":744,"start":0,"stride":2,"freq_min":
                0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,"start":2000,
                "stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]},{"id":
                "calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
                "channels":[{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":
                [[0,0],[200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,
                "freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]}],"processing_blocks":[{"id":
                "pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive","version":
                "0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime",
                "id":"test_realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003",
                "workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":
                [{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004"
                ,"workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},"parameters":{},"dependencies":
                [{"pb_id":"pb-mvp01-20200325-00003","type":["calibration"]}]}]}}

            Note: From Jive, enter above input string without any space.

            :return: A tuple containing a return code and a string in JSON format on successful assignment
             of given resources. The JSON string contains following values:

                dish:
                    Mandatory JSON object consisting of

                    receptorIDList_success:
                        DevVarStringArray
                        Contains ids of the receptors which are successfully allocated. Empty on unsuccessful
                        allocation.


                Example:
                    {
                    "dish": {
                    "receptorIDList_success": ["0001", "0002"]
                    }
                    }

            :rtype: (ResultCode, str)

            :raises: DevFailed when the API fails to allocate resources.

            Note: Enter input without spaces as:{"dish":{"receptorIDList_success":["0001","0002"]}}

            """
            receptorIDList = []
            exception_message = []
            exception_count = 0
            argout = []
            device = self.target

            ## Validate the input JSON string.
            try:
                self.logger.info("Validating input string.")
                input_validator = AssignResourceValidator(device.TMMidSubarrayNodes, device._dish_leaf_node_devices,
                                                          device.DishLeafNodePrefix, self.logger)
                json_argument = input_validator.loads(argin)

                # Create subarray proxy
                subarrayID = int(json_argument['subarrayID'])
                subarrayProxy = device.subarray_FQDN_dict[subarrayID]
                ## check for duplicate allocation
                self.logger.info("Checking for resource reallocation.")
                device._check_receptor_reassignment(json_argument["dish"]["receptorIDList"])
                self.logger.info("device._subarray_allocation: %s", str(device._subarray_allocation))

                ## Allocate resources to subarray
                # Remove Subarray Id key from input json argument and send the json with
                # receptor Id list and SDP block to TMC Subarray Node
                self.logger.info("Allocating resource to subarray %d", subarrayID)
                input_json_subarray = json_argument.copy()
                del input_json_subarray["subarrayID"]
                input_to_sa = json.dumps(input_json_subarray)

                resources_allocated_return = subarrayProxy.command_inout(
                    const.CMD_ASSIGN_RESOURCES, input_to_sa)
                self.logger.debug("resources_allocated_return: %s", resources_allocated_return)

                resources_allocated = resources_allocated_return[1]
                log_msg = "resources_assigned:" + str(resources_allocated)
                self.logger.debug(log_msg)

                # Update self._subarray_allocation variable to update subarray allocation
                # for the related dishes.
                # Also append the allocated dish to out argument.
                for dish in range(0, len(resources_allocated)):
                    dish_ID = "dish" + (resources_allocated[dish])
                    device._subarray_allocation[dish_ID] = "SA" + str(subarrayID)
                    receptorIDList.append(resources_allocated[dish])
                self.logger.info("device._subarray_allocation: %s", str(device._subarray_allocation))

                # Allocation successful
                device._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
                self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

                # Prepare output argument
                argout = {
                    "dish": {
                        "receptorIDList_success": receptorIDList
                    }
                }
                self.logger.debug(argout)
            except (InvalidJSONError, ResourceNotPresentError, SubarrayNotPresentError) as error:
                self.logger.exception("Exception in AssignResource(): %s", str(error))
                device._read_activity_message = "Exception in validating input: " + str(error)
                exception_message.append(const.STR_RESOURCE_ALLOCATION_FAILED + " " + str(error))
                device.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)
            except ResourceReassignmentError as resource_error:
                self.logger.exception("List of the dishes that are already allocated: %s", \
                                      str(resource_error.resources_reallocation))
                device._read_activity_message = const.STR_DISH_DUPLICATE + str(resource_error.resources_reallocation)
                exception_message.append(const.STR_RESOURCE_ALLOCATION_FAILED + str(resource_error))
                device.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)
            except ValueError as ve:
                self.logger.exception("Exception in AssignResources command: %s", str(ve))
                device._read_activity_message = "Invalid value in input: " + str(ve)
                exception_message.append("Invalid value in input: " + str(ve))
                device.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                        exception_message,
                                                                                        exception_count,
                                                                                        const.ERR_ASSGN_RESOURCES)
                device.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)

            message = json.dumps(argout)
            self.logger.info(message)
            return (ResultCode.OK, message)

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
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        AssignResources command invokes the AssignResources command on lower level devices.
        """
        handler = self.get_command_object("AssignResources")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class ReleaseResourcesCommand(ResponseCommand):
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

            if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,]:
                tango.Except.throw_exception("Command ReleaseResources is not allowed in current state.",
                                             "Failed to invoke ReleaseResources command on CentralNode.",
                                             "CentralNode.ReleaseResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def do(self, argin):
            """
            Release all the resources assigned to the given Subarray. It accepts the subarray id, releaseALL flag and
            receptorIDList in JSON string format. When the releaseALL flag is True, ReleaseAllResources command
            is invoked on the respective SubarrayNode. In this case, the receptorIDList tag is empty as all
            the resources of the Subarray are to be released.
            When releaseALL is False, ReleaseResources will be invoked on the SubarrayNode and the resources provided
            in receptorIDList tag, are to be released from the Subarray. The selective release of the resources when
            releaseALL Flag is False is not yet supported.

            :param argin: The string in JSON format. The JSON contains following values:

                subarrayID:
                    DevShort. Mandatory.

                releaseALL:
                    Boolean(True or False). Mandatory. True when all the resources to be released from Subarray.

                receptorIDList:
                    DevVarStringArray. Empty when releaseALL tag is True.

                Example:
                    {
                        "subarrayID": 1,
                        "releaseALL": true,
                        "receptorIDList": []
                    }

                Note: From Jive, enter input as:
                    {"subarrayID":1,"releaseALL":true,"receptorIDList":[]} without any space.

            :return: A tuple containing a return code and a string in josn format on successful release
             of all the resources. The JSON string contains following values:

                releaseALL:
                    Boolean(True or False). If True, all the resources are successfully released from the
                    Subarray.

                receptorIDList:
                    DevVarStringArray. If releaseALL is True, receptorIDList is empty. Else list returns
                    resources (device names) that are noe released from the subarray.

                Example:
                    argout =
                    {
                        "ReleaseAll" : True,
                        "receptorIDList" : []
                    }

             :rtype: (ResultCode, str)

             :raises: ValueError if input argument json string contains invalid value
                    KeyError if input argument json string contains invalid key
                    DevFailed if the command execution or command invocation on SubarrayNode is not successful

            """
            device = self.target
            exception_count = 0
            exception_message = []
            try:
                release_success = False
                jsonArgument = json.loads(argin)
                subarrayID = jsonArgument['subarrayID']
                subarrayProxy = device.subarray_FQDN_dict[subarrayID]
                subarray_name = "SA" + str(subarrayID)
                if jsonArgument['releaseALL'] == True:
                    # Invoke "ReleaseAllResources" on SubarrayNode
                    return_val = subarrayProxy.command_inout(const.CMD_RELEASE_RESOURCES)
                    res_not_released = ast.literal_eval(return_val[1][0])
                    log_msg = "\n\n res_not_released:" + str(res_not_released)
                    self.logger.info()
                    log_msg = const.STR_REL_RESOURCES
                    device._read_activity_message = log_msg
                    if not res_not_released:
                        release_success = True
                        for Dish_ID, Dish_Status in device.subarray_allocation.items():
                            if Dish_Status == subarray_name:
                                device._subarray_allocation[Dish_ID] = "NOT_ALLOCATED"
                        argout = {
                            "ReleaseAll": release_success,
                            "receptorIDList": res_not_released
                        }
                        message = json.dumps(argout)
                        self.logger.info(message)
                        return (ResultCode.OK, message)
                    else:
                        log_msg = const.STR_LIST_RES_NOT_REL + str(res_not_released)
                        device._read_activity_message = log_msg
                        self.logger.info(log_msg)
                        # release_success = False
                else:
                    device._read_activity_message = const.STR_FALSE_TAG
                    self.logger.info(const.STR_FALSE_TAG)

            except ValueError as value_error:
                self.logger.error(const.ERR_INVALID_JSON)
                device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            except KeyError as key_error:
                self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                          exception_message,
                                                                                          exception_count,
                                                                                          const.ERR_RELEASE_RESOURCES)
                device._read_activity_message = const.ERR_RELEASE_RESOURCES

            if exception_count > 0:
                device.throw_exception(exception_message, const.STR_RELEASE_RES_EXEC)

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
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Release all the resources assigned to the given Subarray.
        """
        handler = self.get_command_object("ReleaseResources")

        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("StowAntennas", self.StowAntennasCommand(*args))
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