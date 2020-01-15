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

import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CentralNode"
sys.path.insert(0, module_path)
# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, DeviceMeta, attribute, command, device_property
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import CONST
from future.utils import with_metaclass
import json
# PROTECTED REGION END #    //  CentralNode.additional_import

__all__ = ["CentralNode", "main"]


class CentralNode(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    Central Node is a coordinator of the complete M&C system.
    """
    # PROTECTED REGION ID(CentralNode.class_variable) ENABLED START #

    def healthStateCallback(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None
        """
        if evt.err is False:
            try:
                health_state = evt.attr_value.value
                if CONST.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    self._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif CONST.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    self._subarray2_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif CONST.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    self._subarray3_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif self.CspMasterLeafNodeFQDN in evt.attr_name:
                    self._csp_master_leaf_health = health_state
                elif self.SdpMasterLeafNodeFQDN in evt.attr_name:
                    self._sdp_master_leaf_health = health_state
                else:
                    self.logger.debug(CONST.EVT_UNKNOWN)
                    # TODO: For future reference
                    # self._read_activity_message = CONST.EVT_UNKNOWN

                if health_state == CONST.ENUM_OK:
                    str_log = CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_OK
                    self.logger.info(str_log)
                    # TODO: For future reference
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                    #                                                            ) + CONST.STR_OK
                elif health_state == CONST.ENUM_DEGRADED:
                    str_log = CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_DEGRADED
                    self.logger.info(str_log)
                    # TODO: For future reference
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                    #                                                            ) + CONST.STR_DEGRADED
                elif health_state == CONST.ENUM_FAILED:
                    str_log = CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_FAILED
                    self.logger.info(str_log)
                    # TODO: For future reference
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(evt.device
                    #                                                            ) + CONST.STR_FAILED
                elif health_state == CONST.ENUM_UNKNOWN:
                    str_log = CONST.STR_HEALTH_STATE + str(evt.device) + CONST.STR_UNKNOWN
                    self.logger.info(str_log)
                    # TODO: For future reference
                    # self._read_activity_message = CONST.STR_HEALTH_STATE + str(
                    #     evt.device) + CONST.STR_UNKNOWN
                else:
                    self.logger.info(CONST.STR_HEALTH_STATE_UNKNOWN_VAL)
                    # TODO: For future reference
                    # self._read_activity_message = CONST.STR_HEALTH_STATE_UNKNOWN_VAL + str(evt)
                # Aggregated Health State
                failed_health_count = 0
                degraded_health_count = 0
                unknown_health_count = 0
                ok_health_count = 0

                # Check the health state of CSP and SDP Master Leaf Nodes
                if (self._csp_master_leaf_health == CONST.ENUM_OK or
                        self._sdp_master_leaf_health == CONST.ENUM_OK ):
                    ok_health_count = 1
                elif (self._csp_master_leaf_health == CONST.ENUM_DEGRADED or
                        self._sdp_master_leaf_health == CONST.ENUM_DEGRADED):
                    degraded_health_count = 1
                elif (self._csp_master_leaf_health == CONST.ENUM_FAILED or
                        self._sdp_master_leaf_health == CONST.ENUM_FAILED ):
                    failed_health_count = 1
                else:
                    unknown_health_count = 1

                for value in list(self.subarray_health_state_map.values()):
                    if value == CONST.ENUM_FAILED:
                        failed_health_count = failed_health_count + 1
                        break
                    elif value == CONST.ENUM_DEGRADED:
                        degraded_health_count = degraded_health_count + 1
                    elif value == CONST.ENUM_UNKNOWN:
                        unknown_health_count = unknown_health_count + 1
                    else:
                        ok_health_count = ok_health_count + 1
                if ok_health_count == len(list(self.subarray_health_state_map.values())) + 2:
                    self._telescope_health_state = CONST.ENUM_OK
                elif failed_health_count != 0:
                    self._telescope_health_state = CONST.ENUM_FAILED
                elif degraded_health_count != 0:
                    self._telescope_health_state = CONST.ENUM_DEGRADED
                else:
                    self._telescope_health_state = CONST.ENUM_UNKNOWN
            except KeyError as key_error:
                # TODO: For future reference
                # self._read_activity_message = CONST.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
                self.logger.critical(CONST.ERR_SUBARRAY_HEALTHSTATE)
            except DevFailed as dev_failed:
                # TODO: For future reference
                # self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                self.logger.error(CONST.ERR_SUBSR_SA_HEALTH_STATE)
            except Exception as except_occured:
                # TODO: For future reference
                # self._read_activity_message = CONST.ERR_AGGR_HEALTH_STATE + str(except_occured)
                self.logger.critical(CONST.ERR_AGGR_HEALTH_STATE)
        else:
            # TODO: For future reference
            # self._read_activity_message = CONST.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
            self.logger.critical(CONST.ERR_SUBSR_SA_HEALTH_STATE)
    # PROTECTED REGION END #    //  CentralNode.class_variable

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
        tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)
        self.logger.error(CONST.STR_CMD_FAILED)

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
    )

    NumDishes = device_property(
        dtype='uint', default_value=1,
        doc="Number of Dishes",
    )

    DishLeafNodePrefix = device_property(
        dtype='str', doc="Device name prefix for Dish Leaf Node"
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
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="Health state of Telescope",
    )

    subarray1HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="Health state of Subarray1",
    )

    subarray2HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc="Health state of Subarray2",
    )
    subarray3HealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Activity Message",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        # PROTECTED REGION ID(CentralNode.init_device) ENABLED START #
        """ Initializes the attributes and properties of the Central Node. """
        exception_count = 0
        exception_message = []
        try:
            SKABaseDevice.init_device(self)
            self.logger.info("Device initialisating...")
            self._subarray1_health_state = CONST.ENUM_OK
            self._subarray2_health_state = CONST.ENUM_OK
            self._subarray3_health_state = CONST.ENUM_OK
            self.set_state(DevState.ON)
            # Initialise Attributes
            self._health_state = CONST.ENUM_OK
            self._admin_mode = CONST.ENUM_ONLINE
            self._telescope_health_state = CONST.ENUM_OK
            self.subarray_health_state_map = {}
            self._dish_leaf_node_devices = []
            self._leaf_device_proxy = []
            self.subarray_FQDN_dict = {}
            self._subarray_allocation = {}
            self.set_status(CONST.STR_INIT_SUCCESS)
            self.logger.debug(CONST.STR_INIT_SUCCESS)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed, exception_message,\
                                                                    exception_count,CONST.ERR_INIT_PROP_ATTR_CN)

        #  Get Dish Leaf Node devices List
        # TODO: Getting DishLeafNode devices list from TANGO DB
        # self.tango_db = PyTango.Database()
        # try:
        #     self.dev_dbdatum = self.tango_db.get_device_exported(CONST.GET_DEVICE_LIST_TANGO_DB)
        #     self._dish_leaf_node_devices.extend(self.dev_bdatum.value_string)
        #     print self._dish_leaf_node_devices
        #
        # except Exception as except_occured:
        #     print CONST.ERR_IN_READ_DISH_LN_DEVS, except_occured
        #     self._read_activity_message = CONST.ERR_IN_READ_DISH_LN_DEVS + str(except_occured)
        #     self.dev_logging(CONST.ERR_IN_READ_DISH_LN_DEVS, int(tango.LogLevel.LOG_ERROR))


        for dish in range(1, (self.NumDishes+1)):
            # Update self._dish_leaf_node_devices variable
            self._dish_leaf_node_devices.append(self.DishLeafNodePrefix + "000" + str(dish))

            # Initialize self.subarray_allocation variable to indicate availability of the dishes
            dish_ID = "dish000" + str(dish)
            self._subarray_allocation[dish_ID] = "NOT_ALLOCATED"

        # Create proxies of Dish Leaf Node devices
        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy.append(DeviceProxy(self._dish_leaf_node_devices[name]))
            except (DevFailed, KeyError) as except_occurred:
                [exception_message, exception_count] = self._handle_devfailed_exception(except_occurred,
                                                exception_message, exception_count,CONST.ERR_IN_CREATE_PROXY)

        # Create device proxy for CSP Master Leaf Node
        try:
            self._csp_master_leaf_proxy = DeviceProxy(self.CspMasterLeafNodeFQDN)
            self._csp_master_leaf_proxy.subscribe_event(CONST.EVT_SUBSR_CSP_MASTER_HEALTH,
                                                        EventType.CHANGE_EVENT,
                                                        self.healthStateCallback, stateless=True)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                    exception_message, exception_count,CONST.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH)


        # Create device proxy for SDP Master Leaf Node
        try:
            self._sdp_master_leaf_proxy = DeviceProxy(self.SdpMasterLeafNodeFQDN)
            self._sdp_master_leaf_proxy.subscribe_event(CONST.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                        EventType.CHANGE_EVENT,
                                                        self.healthStateCallback, stateless=True)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                exception_message, exception_count,CONST.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH)


        for subarray in range(0, len(self.TMMidSubarrayNodes)):
            try:
                subarray_proxy = DeviceProxy(self.TMMidSubarrayNodes[subarray])
                self.subarray_health_state_map[subarray_proxy] = -1
                subarray_proxy.subscribe_event(CONST.EVT_SUBSR_HEALTH_STATE,
                                               EventType.CHANGE_EVENT,
                                               self.healthStateCallback, stateless=True)

                #populate subarrayID-subarray proxy mapsubarray_proxy
                tokens = self.TMMidSubarrayNodes[subarray].split('/')
                subarrayID = int(tokens[2])
                self.subarray_FQDN_dict[subarrayID] = subarray_proxy
                print("Hii Akash subarrays proxy dict:",self.subarray_FQDN_dict)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count,CONST.ERR_SUBSR_SA_HEALTH_STATE)


        # PROTECTED REGION END #    //  CentralNode.init_device

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

    @command(
        dtype_in=('str',),
        doc_in="List of Receptors to be stowed",
    )
    @DebugIt()
    def StowAntennas(self, argin):
        # PROTECTED REGION ID(CentralNode.StowAntennas) ENABLED START #
        """
        Stows the specified receptors.

        :param argin: List of Receptors to be stowed.

        :return: None
        """
        exception_count = 0
        exception_message = []
        try:
            for leafId in range(0, len(argin)):
                if type(float(argin[leafId])) == float:
                    pass
            self.logger.info(CONST.STR_STOW_CMD_ISSUED_CN)
            self._read_activity_message = CONST.STR_STOW_CMD_ISSUED_CN
            for i in range(0, len(argin)):
                device_name = self.DishLeafNodePrefix + argin[i]
                try:
                    device_proxy = DeviceProxy(device_name)
                    device_proxy.command_inout(CONST.CMD_SET_STOW_MODE)
                except DevFailed as dev_failed:
                    [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                                exception_message, exception_count,  CONST.ERR_EXE_STOW_CMD)

                # throw exception:
                if exception_count > 0:
                    self.throw_exception(exception_message, CONST.STR_STOW_ANTENNA_EXEC)

        except ValueError as value_error:
            self.logger.error(CONST.ERR_STOW_ARGIN)
            self._read_activity_message = CONST.ERR_STOW_ARGIN + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except Exception as except_occured:
            [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                exception_message, exception_count, CONST.ERR_EXE_STOW_CMD)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_STOW_ANTENNA_EXEC)
        # PROTECTED REGION END #    //  CentralNode.stow_antennas

    @command(
    )
    @DebugIt()
    def StandByTelescope(self):
        # PROTECTED REGION ID(CentralNode.StandByTelescope) ENABLED START #
        """ Set the Elements into STANDBY state (i.e. Low Power State). """
        exception_count =0
        exception_message =[]
        self.logger.info(CONST.STR_STANDBY_CMD_ISSUED)
        self._read_activity_message = CONST.STR_STANDBY_CMD_ISSUED
        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy[name].command_inout(CONST.CMD_SET_STANDBY_MODE)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_EXE_STANDBY_CMD)

        try:
            self._csp_master_leaf_proxy.command_inout(CONST.CMD_STANDBY, [])
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_EXE_STANDBY_CMD)


        try:
            self._sdp_master_leaf_proxy.command_inout(CONST.CMD_STANDBY)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_EXE_STANDBY_CMD)
        try:
            self.subarrayProxy.command_inout(CONST.CMD_STARTUP)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message,exception_count, CONST.ERR_EXE_STARTUP_CMD)
            # throw exception:
            if exception_count > 0:
                self.throw_exception(exception_message, CONST.STR_STANDBY_EXEC)
        # PROTECTED REGION END #    //  CentralNode.standby_telescope

    @command(
    )
    @DebugIt()
    def StartUpTelescope(self):
        # PROTECTED REGION ID(CentralNode.StartUpTelescope) ENABLED START #
        """ Setting the startup state to TRUE enables the telescope to accept subarray commands as per the subarray
        model.Set the Elements into ON state from STANDBY state. """
        exception_count =0
        exception_message = []
        self.logger.info(CONST.STR_STARTUP_CMD_ISSUED)
        self._read_activity_message = CONST.STR_STARTUP_CMD_ISSUED
        for name in range(0, len(self._dish_leaf_node_devices)):
            try:
                self._leaf_device_proxy[name].command_inout(CONST.CMD_SET_OPERATE_MODE)
            except DevFailed as dev_failed:
                [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_EXE_STARTUP_CMD)


        try:
            self._csp_master_leaf_proxy.command_inout(CONST.CMD_STARTUP,
                                                      [])
        except Exception as except_occured:
            [exception_message, exception_count] = self._handle_generic_exception(except_occured,
                                                exception_message, exception_count, CONST.ERR_EXE_STARTUP_CMD)
        try:
            self._sdp_master_leaf_proxy.command_inout(CONST.CMD_STARTUP)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_EXE_STARTUP_CMD)

        for subarray in range(0, len(self.TMMidSubarrayNodes)):
            try:
                subarray_proxy = DeviceProxy(self.TMMidSubarrayNodes[subarray])
                self.subarray_health_state_map[subarray_proxy] = -1
                subarray_proxy.subscribe_event(CONST.EVT_SUBSR_HEALTH_STATE,
                                               EventType.CHANGE_EVENT,
                                               self.healthStateCallback, stateless=True)

                # populate subarrayID-subarray proxy mapsubarray_proxy
                tokens = self.TMMidSubarrayNodes[subarray].split('/')
                subarrayID = int(tokens[2])
                self.subarray_FQDN_dict[subarrayID] = subarray_proxy
            except DevFailed as dev_failed:
                [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_EXE_STARTUP_CMD)

            if exception_count > 0:
                self.throw_exception(exception_message, CONST.STR_STARTUP_EXEC)

        # PROTECTED REGION END #    //  CentralNode.startup_telescope

    @command(
        dtype_in='str',
        doc_in="The string in JSON format. The JSON contains following values:\nsubarrayID: "
        "DevShort\ndish: JSON object consisting\n- receptorIDList: DevVarStringArray. "
        "The individual string should contain dish numbers in string format with "
        "preceding zeroes upto 3 digits. E.g. 0001, 0002",
        dtype_out='str',
        doc_out="The string in JSON format. The JSON contains following values:\ndish:"
        " JSON object consisting receptors allocated successfully: DevVarStringArray."
        " The individual string should contain dish numbers in string format with "
        "preceding zeroes upto 3 digits. E.g. 0001, 0002", )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(CentralNode.AssignResources) ENABLED START #
        """
        Assigns resources to given subarray. It accepts the subarray id and
        receptor id list in JSON string format. Upon successful execution, the
        'receptorIDList' attribute of the given subarray is populated with the given
        receptors.Also checking for duplicate allocation of resources is done. If already allocated it will throwout
        error message regarding t he prior existence of resource.

        :param argin: The string in JSON format. The JSON contains following values:


            subarrayID:
                DevShort. Mandatory.

            dish:
                Mandatory JSON object consisting of

                receptorIDList:
                    DevVarStringArray
                    The individual string should contain dish numbers in string format
                    with preceding zeroes upto 3 digits. E.g. 0001, 0002.

            Example:
                {
                "subarrayID": 1,
                "dish": {
                "receptorIDList": ["0001", "0002"]
                }
                }

        Note: From Jive, enter input as:
        {"subarrayID":1,"dish":{"receptorIDList":["0001"]}} without any space.

        :return: The string in JSON format. The JSON contains following values:

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
            Note: Enter input without spaces as:{"dish":{"receptorIDList_success":["0001","0002"]}}
        """
        receptorIDList = []
        exception_message = []
        exception_count = 0
        argout = []
        try:
            # serialize the json
            jsonArgument = json.loads(argin)
            # Create subarray proxy
            subarrayID = int(jsonArgument['subarrayID'])
            subarrayProxy = self.subarray_FQDN_dict[subarrayID]
            # Check for the duplicate receptor allocation
            duplicate_allocation_count = 0
            duplicate_allocation_dish_ids = []
            input_receptor_list = jsonArgument["dish"]["receptorIDList"]
            len_input_receptor_list= len(input_receptor_list)
            for dish in range(0, len_input_receptor_list):
                dish_ID = "dish" + input_receptor_list[dish]
                if self._subarray_allocation[dish_ID] != "NOT_ALLOCATED":
                    duplicate_allocation_dish_ids.append(dish_ID)
                    duplicate_allocation_count = duplicate_allocation_count + 1
            if duplicate_allocation_count == 0:
                self._resources_allocated = subarrayProxy.command_inout(
                    CONST.CMD_ASSIGN_RESOURCES, jsonArgument["dish"]["receptorIDList"])
                # Update self._subarray_allocation variable to update subarray allocation
                # for the related dishes.
                # Also append the allocated dish to out argument.
                for dish in range(0, len(self._resources_allocated)):
                    dish_ID = "dish" + (self._resources_allocated[dish])
                    self._subarray_allocation[dish_ID] = "SA" + str(subarrayID)
                    receptorIDList.append(self._resources_allocated[dish])
                self._read_activity_message = CONST.STR_ASSIGN_RESOURCES_SUCCESS
                self.logger.info(CONST.STR_ASSIGN_RESOURCES_SUCCESS)
                argout = {
                    "dish": {
                        "receptorIDList_success": receptorIDList
                    }
                }
            else:
                self._read_activity_message = CONST.STR_DISH_DUPLICATE+ str(duplicate_allocation_dish_ids)
                argout = {
                    "dish": {
                        "receptorIDList_success": receptorIDList
                    }
                }
        except ValueError as value_error:
            self.logger.error(CONST.ERR_INVALID_JSON)
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        except KeyError as key_error:
            self.logger.error(CONST.ERR_JSON_KEY_NOT_FOUND)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                                exception_message, exception_count,CONST.ERR_ASSGN_RESOURCES)

        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, CONST.ERR_ASSGN_RESOURCES)

        #throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_ASSIGN_RES_EXEC)
            argout = '{"dish": {"receptorIDList_success": []}}'

        # For future reference
        #argout['dish']['receptorIDList'] = receptorIDList
        #argout['receptorIDList'] = receptorIDList
        return json.dumps(argout)
        # PROTECTED REGION END #    //  CentralNode.AssignResources

    @command(dtype_in='str', dtype_out='str', )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(CentralNode.ReleaseResources) ENABLED START #

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

            :return: argout: The string in JSON format. The JSON contains following values:

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
        """
        exception_count = 0
        exception_message =[]
        try:
            release_success = False
            res_not_released = []
            jsonArgument = json.loads(argin)
            subarrayID = jsonArgument['subarrayID']
            subarrayProxy = self.subarray_FQDN_dict[subarrayID]
            subarray_name = "SA" + str(subarrayID)
            if jsonArgument['releaseALL'] == True:
                res_not_released = subarrayProxy.command_inout(CONST.CMD_RELEASE_RESOURCES)
                self._read_activity_message = CONST.STR_REL_RESOURCES

                self.logger.info(CONST.STR_REL_RESOURCES)
                if not res_not_released:
                    release_success = True
                    for Dish_ID, Dish_Status in self._subarray_allocation.items():
                        if Dish_Status == subarray_name:
                            self._subarray_allocation[Dish_ID] = "NOT_ALLOCATED"
                else:
                    self._read_activity_message = CONST.STR_LIST_RES_NOT_REL \
                                                  + res_not_released
                    release_success = False
            else:
                self._read_activity_message = CONST.STR_FALSE_TAG
        except ValueError as value_error:
            self.logger.error(CONST.ERR_INVALID_JSON)
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except KeyError as key_error:
            self.logger.error(CONST.ERR_JSON_KEY_NOT_FOUND)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count,  CONST.ERR_RELEASE_RESOURCES)


        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_RELEASE_RES_EXEC)

        argout = {
            "ReleaseAll" : release_success,
            "receptorIDList" : res_not_released
        }
        return json.dumps(argout)
        # PROTECTED REGION END #    //  CentralNode.ReleaseResource
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

