"""
CSP Subarray Leaf node is monitors the CSP Subarray and issues control actions during an observation.
It also acts as a CSP contact point for Subarray Node for observation execution for TMC.
"""
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
import datetime
import sys
import os
import threading
import random
import calendar
import time

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarrayLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)

# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, DeviceMeta, attribute, command, device_property
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CspSubarrayLeafNode.additionnal_import) ENABLED START #
from future.utils import with_metaclass
import CONST
import json
# PROTECTED REGION END #    //  CspSubarrayLeafNode.additionnal_import

__all__ = ["CspSubarrayLeafNode", "main"]

class CspSubarrayLeafNode(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    CSP Subarray Leaf node monitors the CSP Subarray and issues control actions during an observation.
    """
    # PROTECTED REGION ID(CspSubarrayLeafNode.class_variable) ENABLED START #

    _DELAY_UPDATE_INTERVAL = 10
    # _stop_delay_model_event = # type: Event

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on CspSubarray.

        :param event: response from CspSubarray for the invoked command

        :return: None

        """
        excpt_count = 0
        excpt_msg = []
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                self.dev_logging(log, int(tango.LogLevel.LOG_ERROR))
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.dev_logging(log, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occurred:
            self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
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
        dtype='str',
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

    cspsubarrayHealthState = attribute(name="cspsubarrayHealthState", label="cspsubarrayHealthState",
                                       forwarded=True
                                      )

    cspSubarrayObsState = attribute(name="cspSubarrayObsState", label="cspSubarrayObsState", forwarded=True)

    # ---------------
    # General methods
    # ---------------
    def delay_model_calculator(self, argin):
        """
        This method calculates the delay model for consumption of CSP subarray.
        This implementation is very ad hoc and require lots of modifications to calculate
        actual delay models.
        Current implementation generates random number for delay values. No delay
        library is used in this code. It also considers four receptors to calculate
        delays. Ideally, the receptor count should be based on the receptors allocated
        to the subarray. Also, currently four frequency slices and six  bands are
        considered for delay calculations. The values of receptors and frequency slice
        ids are also non-standard.
        The epoch value is the current timestamp value.

        :param argin: int.
            The argument contains delay model update interval in seconds.

        :return: None.
        """
        delay_update_interval = argin
        # list of frequency slice ids
        _fsids_list = ["fs1", "fs2", "fs3", "fs4"]
        # list of bands
        _bands_list = ["band1", "band2", "band3", "band4", "band5a", "band5b"]
        # receptor list
        # TBD: This list should be taken from receptor_id_list attribute of subarray node
        _receptor_list = ["d0001", "d0002", "d0003", "d0004"]

        while not self._stop_delay_model_event.isSet():
            if(self.CspSubarrayProxy.obsState == CONST.ENUM_READY
                    or self.CspSubarrayProxy.obsState == CONST.ENUM_SCANNING):

                self.dev_logging("Calculating delays.", int(tango.LogLevel.LOG_INFO))
                delay_model_json = {}
                delay_model = []
                receptor_delay_model = []
                delay_model_per_epoch = {}
                for receptor in _receptor_list:
                    receptor_delay_object = {}
                    receptor_delay_object["receptor"] = receptor
                    receptor_specific_delay_details = []
                    for fsid in _fsids_list:
                        fsid_delay_object = {}
                        fsid_delay_object["fsid"] = fsid
                        delay_coeff_array = []
                        for band in _bands_list:
                            delay_coeff_array.append(random.uniform(0.01, 10))  # random delay
                        fsid_delay_object["delayCoeff"] = delay_coeff_array
                        receptor_specific_delay_details.append(fsid_delay_object)
                    receptor_delay_object["receptorDelayDetails"] = receptor_specific_delay_details
                    receptor_delay_model.append(receptor_delay_object)
                delay_model_per_epoch["epoch"] = calendar.timegm(time.gmtime())
                delay_model_per_epoch["delayDetails"] = receptor_delay_model
                delay_model.append(delay_model_per_epoch)
                delay_model_json["delayModel"] = delay_model
                print("delay_model_json: ", delay_model_json)

                # update the attribute
                self.delay_model_lock.acquire()
                self._delay_model = json.dumps(delay_model_json)
                self.delay_model_lock.release()

                # wait for timer event
                self._stop_delay_model_event.wait(delay_update_interval)
            else:
                self._delay_model = " "

        print("Stop event received. Thread exit.")
        self.dev_logging("Stop event received. Thread exit.", int(tango.LogLevel.LOG_INFO))

    def init_device(self):
        """
        Initializes the attributes and properties of the CspSubarrayLeafNode.
        """
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CspSubarrayLeafNode.init_device) ENABLED START #

        try:
            self._state = 0
            # create subarray Proxy
            self.CspSubarrayProxy = DeviceProxy(self.CspSubarrayNodeFQDN)
            self._read_activity_message = " "
            self._delay_model = " "
            self._visdestination_address = " "

            ## Start thread to update delay model ##
            # Create event
            self._stop_delay_model_event = threading.Event()
            #
            # create lock
            self.delay_model_lock = threading.Lock()

            # create thread
            self.dev_logging("Starting thread to calculate delay model.", int(tango.LogLevel.LOG_INFO))
            self.delay_model_calculator_thread = threading.Thread(
                target=self.delay_model_calculator,
                args=[self._DELAY_UPDATE_INTERVAL],
                daemon=False)
            self.delay_model_calculator_thread.start()

            self.set_state(DevState.ON)
            self.set_status(CONST.STR_CSPSALN_INIT_SUCCESS)
            self._csp_subarray_health_state = CONST.ENUM_OK
            self._opstate = CONST.ENUM_INIT
            self.dev_logging(CONST.STR_CSPSALN_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except DevFailed as dev_failed:
            print(CONST.ERR_INIT_PROP_ATTR_CSPSALN)
            self._read_activity_message = CONST.ERR_INIT_PROP_ATTR_CSPSALN
            self.dev_logging(CONST.ERR_INIT_PROP_ATTR_CSPSALN, int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            print(CONST.STR_ERR_MSG, dev_failed)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # Stop thread to update delay model
        self.dev_logging("Stopping delay model thread.", int(tango.LogLevel.LOG_INFO))
        self._stop_delay_model_event.set()
        self.delay_model_calculator_thread.join()
        self.dev_logging("Exiting.", int(tango.LogLevel.LOG_INFO))
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_state(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.state_read) ENABLED START #
        "Returns the state of device."
        return self._state
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.state_read

    def read_delayModel(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_read) ENABLED START #
        "Returns the delay model."
        return self._delay_model
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_read

    def write_delayModel(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_write) ENABLED START #
        "Sets in to the delay model."
        self._delay_model = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_write

    def read_visDestinationAddress(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_read) ENABLED START #
        "Returns the destination address."
        return self._visdestination_address
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_read

    def write_visDestinationAddress(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_write) ENABLED START #
        "Sets the destination address."
        self._visdestination_address = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_write

    def read_versionInfo(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.versionInfo_read) ENABLED START #
        "Returns the version information."
        return ''
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_read) ENABLED START #
        "Returns activity message."
        return self._read_activity_message
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_write) ENABLED START #
        "Sets the activity message."
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_write

    def read_opState(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.opState_read) ENABLED START #
        "Returns the OpState."
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
        """
        This command configures the scan. It accepts configuration capabilities in JSON string format and
        invokes ConfigureScan command on CspSubarray with configuration capabilities in JSON string as an
        input argument.

        :param argin: The string in JSON format. The JSON contains following values:

            Example:
                {
                  "csp":
                  {
                     "frequencyBand": "1",
                     "delayModelSubscriptionPoint": "",
                     "visDestinationAddressSubscriptionPoint": "",
                     "fsp": [
                    {
                      "fspID": "1",
                      "functionMode": "CORR",
                      "frequencySliceID": 1,
                      "integrationTime": 1400,
                      "corrBandwidth": 0,
                      "channelAveragingMap": []
                    },
                    {
                      "fspID": "2",
                      "functionMode": "CORR",
                      "frequencySliceID": 1,
                      "integrationTime": 1400,
                      "corrBandwidth": 0,
                      "channelAveragingMap": []
                     }
                    ]
                   }
                 }

        Note: \n
        from Jive, enter input as :\n
        {"csp":{"frequencyBand":"1","delayModelSubscriptionPoint": "","visDestinationAddressSubscriptionPoint"
        :"",,"fsp":[{"fspID":"1","functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,
        "corrBandwidth":0,"channelAveragingMap":[]},{"fspID":"2","functionMode":"CORR","frequencySliceID":1,
        "integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[]}]}}
        without white spaces

        :return: None.
        """
        excpt_msg = []
        excpt_count = 0
        try:
            json.loads(argin)
            self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_CONFIGURESCAN, argin, self.commandCallback)
            self._read_activity_message = CONST.STR_CONFIGURESCAN_SUCCESS
            self.dev_logging(CONST.STR_CONFIGURESCAN_SUCCESS, int(tango.LogLevel.LOG_INFO))
            self.dev_logging(argin, int(tango.LogLevel.LOG_DEBUG))

        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON_CONFIG_SCAN + str(value_error),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON_CONFIG_SCAN + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_CONFIGURESCAN_INVOKING_CMD + str(dev_failed),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_CONFIGURESCAN_INVOKING_CMD + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_CONFIGURESCAN_INVOKING_CMD  + str(except_occurred),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_CONFIGURESCAN_INVOKING_CMD  + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_CONFIG_SCAN_EXEC, tango.ErrSeverity.ERR)


        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ConfigureScan

    @command(
        dtype_in=('str',),
    )
    @DebugIt()
    def StartScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.StartScan) ENABLED START #
        """
        This command invokes Scan command on CspSubarray. It is allowed only when CspSubarray is in READY
        state.

        :param argin: JSON string consists of scanDuration (int).

        Example: in jive:{"scanDuration": 10.0}

        :return: None.
        """
        excpt_msg = []
        excpt_count = 0
        try:
            json_scan_duration = json.loads(argin[0])
            scan_duration = json_scan_duration["scanDuration"]
            #Check if CspSubarray is in READY state
            if self.CspSubarrayProxy.obsState == CONST.ENUM_READY:
                #Invoke StartScan command on CspSubarray
                self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_STARTSCAN, "0", self.commandCallback)
                self._read_activity_message = CONST.STR_STARTSCAN_SUCCESS
                self.dev_logging(CONST.STR_STARTSCAN_SUCCESS, int(tango.LogLevel.LOG_INFO))
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_READY
                self.dev_logging(CONST.ERR_DEVICE_NOT_READY, int(tango.LogLevel.LOG_ERROR))

        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_STARTSCAN_RESOURCES + str(dev_failed),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_STARTSCAN_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_STARTSCAN_RESOURCES  + str(except_occurred),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_STARTSCAN_RESOURCES  + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_START_SCAN_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.StartScan


    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.EndScan) ENABLED START #
        """
        It invokes EndScan command on CspSubarray. This command is allowed when CspSubarray is in SCANNING
        state.

        :return: None.
        """
        excpt_msg = []
        excpt_count = 0
        try:
            if self.CspSubarrayProxy.obsState == CONST.ENUM_SCANNING:
                # Invoke EndScan command on CspSubarray
                self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_ENDSCAN, self.commandCallback)
                self._read_activity_message = CONST.STR_ENDSCAN_SUCCESS
                self.dev_logging(CONST.STR_ENDSCAN_SUCCESS, int(tango.LogLevel.LOG_INFO))
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_IN_SCAN
                self.dev_logging(CONST.ERR_DEVICE_NOT_IN_SCAN, int(tango.LogLevel.LOG_ERROR))

        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_ENDSCAN_INVOKING_CMD + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ENDSCAN_INVOKING_CMD + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_ENDSCAN_INVOKING_CMD + str(except_occurred),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ENDSCAN_INVOKING_CMD + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_ENDSCAN_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def ReleaseAllResources(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ReleaseResources) ENABLED START #
        """
        It invokes RemoveAllReceptors command on CspSubarray and releases all the resources assigned to
        CspSubarray.

        :return: None.
        """
        excpt_msg = []
        excpt_count = 0
        try:
            #Invoke RemoveAllReceptors command on CspSubarray
            self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_REMOVE_ALL_RECEPTORS, self.commandCallback)
            self._read_activity_message = CONST.STR_REMOVE_ALL_RECEPTORS_SUCCESS
            self.dev_logging(CONST.STR_REMOVE_ALL_RECEPTORS_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_RELEASE_ALL_RESOURCES + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_RELEASE_ALL_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_RELEASE_ALL_RESOURCES  + str(except_occurred),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_RELEASE_ALL_RESOURCES  + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_RELEASE_RES_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ReleaseResources

    @command(
        dtype_in=('str',),
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.AssignResources) ENABLED START #
        """
        It accepts receptor id list in JSON string format and invokes AddReceptors command on CspSubarray
        with receptorIDList (list of integers) as an input argument.

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
            #Parse receptorIDList from JSON string.
            jsonArgument = json.loads(argin[0])
            receptorIDList = jsonArgument[CONST.STR_DISH][CONST.STR_RECEPTORID_LIST]
            print ("Assign Resources command called", receptorIDList)
            #convert receptorIDList from list of string to list of int
            for i in range(0, len(receptorIDList)):
                receptorIDList[i] = int(receptorIDList[i])

            #Invoke AddReceptors command on CspSubarray
            self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_ADD_RECEPTORS, receptorIDList,
                                                       self.commandCallback)
            self._read_activity_message = CONST.STR_ADD_RECEPTORS_SUCCESS
            self.dev_logging(CONST.STR_ADD_RECEPTORS_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON_ASSIGN_RES + str(value_error),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
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

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.EndSB) ENABLED START #
        """
        This command invokes EndSB command on CSP Subarray in order to end current scheduling block.

        :return: None.

        """
        excpt_msg = []
        excpt_count = 0
        try:
            if self.CspSubarrayProxy.obsState == CONST.ENUM_READY:
                self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_ENDSB, self.commandCallback)
                self._read_activity_message = CONST.STR_ENDSB_SUCCESS
                self.dev_logging(CONST.STR_ENDSB_SUCCESS, int(tango.LogLevel.LOG_INFO))
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_READY
                self.dev_logging(CONST.ERR_DEVICE_NOT_READY, int(tango.LogLevel.LOG_ERROR))
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_ENDSB_INVOKING_CMD + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ENDSB_INVOKING_CMD + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_ENDSB_INVOKING_CMD + str(except_occurred), int(tango.LogLevel.
                                                                                      LOG_ERROR))
            self._read_activity_message = CONST.ERR_ENDSB_INVOKING_CMD + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_ENDSB_EXEC, tango.ErrSeverity.ERR)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.EndSB

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

if __name__ == '__main__':
    main()
