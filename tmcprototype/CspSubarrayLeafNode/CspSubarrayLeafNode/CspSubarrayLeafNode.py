# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, DeviceMeta, attribute, command, device_property
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CspSubarrayLeafNode.additionnal_import) ENABLED START #
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarrayLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)

import json
import CONST
# PROTECTED REGION END #    //  CspSubarrayLeafNode.additionnal_import

__all__ = ["CspSubarrayLeafNode", "main"]


class CspSubarrayLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CspSubarrayLeafNode.class_variable) ENABLED START #

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on DishMaster.
        :param event: response from DishMaster for the invoked command
        :return: None

        """
        excpt_count = 0
        excpt_msg = []
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                print(log)
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                self.dev_logging(log, int(tango.LogLevel.LOG_ERROR))
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                print(log)
                self._read_activity_message = log
                self.dev_logging(log, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occurred:
            self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            print(self._read_activity_message)
            self.dev_logging(CONST.ERR_EXCEPT_CMD_CB, int(tango.LogLevel.LOG_ERROR))
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # Throw Exception
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_CMD_CALLBK, tango.ErrSeverity.ERR)
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------






    CspSubarrayNodeFQDN = device_property(
        dtype='str', default_value="mid-csp/elt/subarray01"
    )

    # ----------
    # Attributes
    # ----------











    state = attribute(
        dtype='DevEnum',
        enum_labels=["INIT", "ON", "ALARM", "FAULT", "UNKNOWN", "DISABLE", ],
    )

    delayModel = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    visDestinationAddress = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    CspSubarrayHealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    versionInfo = attribute(
        dtype='str',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    opState = attribute(
        dtype='DevEnum',
        enum_labels=["INIT", "OFF", "ON", "ALARM", "DISABLE", "FAULT", "UNKNOWN", ],
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CspSubarrayLeafNode.init_device) ENABLED START #
        try:
            self._state = 0
            # create subarray Proxy
            self.subarrayProxy = DeviceProxy(self.CspSubarrayNodeFQDN)
            self._read_activity_message = " "
            self.set_state(DevState.ON)
            self.set_status(CONST.STR_CSPSALN_INIT_SUCCESS)
            self._csp_subarray_health_state = CONST.ENUM_OK
            self._opstate = CONST.ENUM_INIT
            self._delay_model = " "
            self._visdestination_address = " "

        except DevFailed as dev_failed:
            print(CONST.ERR_INIT_PROP_ATTR_CN)
            self._read_activity_message = CONST.ERR_INIT_PROP_ATTR_CN
            self.dev_logging(CONST.ERR_INIT_PROP_ATTR_CN, int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            print(CONST.STR_ERR_MSG, dev_failed)

        # PROTECTED REGION END #    //  CspSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_state(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.state_read) ENABLED START #
        return self._state
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.state_read

    def read_delayModel(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_read) ENABLED START #
        return self._delay_model
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_read

    def write_delayModel(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_write) ENABLED START #
        self._delay_model = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_write

    def read_visDestinationAddress(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_read) ENABLED START #
        return self._visdestination_address
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_read

    def write_visDestinationAddress(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_write) ENABLED START #
        self._visdestination_address = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_write

    def read_CspSubarrayHealthState(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.CspSubarrayHealthState_read) ENABLED START #
        return self._csp_subarray_health_state
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.CspSubarrayHealthState_read

    def read_versionInfo(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.versionInfo_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_write

    def read_opState(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.opState_read) ENABLED START #
        return self._opstate
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.opState_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def ConfigureScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ConfigureScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ConfigureScan

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def StartScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.StartScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.StartScan

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def EndScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.EndScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def ReleaseResources(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ReleaseResources) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ReleaseResources

    @command(
    dtype_in=('str',), 
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.AssignResources) ENABLED START #
        """
        #ToDo :Need to update
        It accepts receptor id list in JSON string format and invokes AssignResources command
        on CspSubarray with receptorIDList (list of integers) as an input argument.

        :param argin: The string in JSON format. The JSON contains following values:

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
                "receptorIDList": ["0001","0002"]
                }
                }

        Note: From Jive, enter input as:
        {"dish":{"receptorIDList":["0001","0002"]}} without any space.

        :return: None.
        """
        excpt_msg = []
        excpt_count = 0
        try:
            jsonArgument = json.loads(argin[0])
            receptorIDList = jsonArgument[CONST.STR_DISH][CONST.STR_RECEPTORID_LIST]

            #convert receptorIDList(list of string) to list of int
            self.subarrayProxy.command_inout_asynch(CONST.CMD_ADD_RECEPTORS, list(map(int, receptorIDList)),
                                                    self.commandCallback)
            self._read_activity_message = CONST.STR_ASSIGN_RESOURCES_SUCCESS
            self.dev_logging(CONST.STR_ASSIGN_RESOURCES_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            #self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_ASSGN_RESOURCES + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ASSGN_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_ASSGN_RESOURCES + str(except_occurred), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ASSGN_RESOURCES + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_ASSIGN_RES_EXEC, tango.ErrSeverity.ERR)

        # PROTECTED REGION END #    //  CspSubarrayLeafNode.AssignResources

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspSubarrayLeafNode.main) ENABLED START #
    return run((CspSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.main

if __name__ == '__main__':
    main()
