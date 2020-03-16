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
from datetime import datetime, timedelta
import pytz
import katpoint
import numpy as np

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarrayLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
ska_antennas_path = os.path.abspath(os.path.join(os.path.join(file_path, os.pardir),os.pardir)) \
                    + "/ska_antennas.txt"
# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, DevState, DevFailed
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
    # _delay_in_advance variable (in seconds) is added to current timestamp and is used to calculate advance
    # delay coefficients.
    _delay_in_advance = 60
    # _stop_delay_model_event = # type: Event

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on CspSubarray.

        :param event: response from CspSubarray for the invoked command

        :return: None

        """
        exception_count = 0
        exception_message = []
        try:
            if event.err:
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                self.logger.error(log)
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.logger.info(log)
        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, CONST.ERR_EXCEPT_CMD_CB)

        # Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_CMD_CALLBK)

    # PROTECTED REGION END #    //  CspSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------
    CspSubarrayFQDN = device_property(
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

    cspsubarrayHealthState = attribute(name="cspsubarrayHealthState", label="cspsubarrayHealthState",
                                       forwarded=True
                                      )

    cspSubarrayObsState = attribute(name="cspSubarrayObsState", label="cspSubarrayObsState", forwarded=True)

    # ---------------
    # General methods
    # ---------------

    def calculate_geometric_delays(self, time_t0):
        """
        This method calculates geometric delay values (in Second) using KATPoint library. It requires delay
        correction object, timestamp t0 and target RaDec.
        Numpy library is used to convert delay values (in Seconds) to fifth order polynomial coefficients.
        Six timestamps from the time-frame t0 to t+10, are used to calculate delays per antenna. These six
        delay values are then used to calculate fifth order polynomial coefficients.
        In order to calculate delays in advance, timestamp t0 is considered to be one minute ahead of the
        the current timestamp.

        :param argin: time_t0
        :return: Dictionary containing fifth order polynomial coefficients per antenna per fsp.
        """

        delay_corrections_h_array_t0 = []
        delay_corrections_h_array_t1 = []
        delay_corrections_h_array_t2 = []
        delay_corrections_h_array_t3 = []
        delay_corrections_h_array_t4 = []
        delay_corrections_h_array_t5 = []
        delay_corrections_h_array_dict = {}
        delay_corrections_v_array_t0 = []
        delay_corrections_v_array_t1 = []
        delay_corrections_v_array_t2 = []
        delay_corrections_v_array_t3 = []
        delay_corrections_v_array_t4 = []
        delay_corrections_v_array_t5 = []
        delay_corrections_v_array_dict = {}

        # Delays are calculated for the timestamps between "t0 - 25" to "t0 + 25" at an interval of 10
        # seconds.
        timestamp_array = [time_t0 - timedelta(seconds=25), (time_t0 - timedelta(seconds=15)),
                           (time_t0 - timedelta(seconds=5)), (time_t0 + timedelta(seconds=5)),
                           (time_t0 + timedelta(seconds=15)), (time_t0 + timedelta(seconds=25))]

        for timestamp_index in range(0, len(timestamp_array)):
            # Calculate geometric delay value.
            delay = self.delay_correction_object._calculate_delays(self.target,
                                                                   str(timestamp_array[timestamp_index]))

            # Horizontal and vertical delay corrections for each antenna
            for i in range(0, len(delay)):
                if i % 2 == 0:
                    if timestamp_index == 0:
                        delay_corrections_h_array_t0.append(delay[i])
                    elif timestamp_index == 1:
                        delay_corrections_h_array_t1.append(delay[i])
                    elif timestamp_index == 2:
                        delay_corrections_h_array_t2.append(delay[i])
                    elif timestamp_index == 3:
                        delay_corrections_h_array_t3.append(delay[i])
                    elif timestamp_index == 4:
                        delay_corrections_h_array_t4.append(delay[i])
                    elif timestamp_index == 5:
                        delay_corrections_h_array_t5.append(delay[i])
                else:
                    if timestamp_index == 0:
                        delay_corrections_v_array_t0.append(delay[i])
                    elif timestamp_index == 1:
                        delay_corrections_v_array_t1.append(delay[i])
                    elif timestamp_index == 2:
                        delay_corrections_v_array_t2.append(delay[i])
                    elif timestamp_index == 3:
                        delay_corrections_v_array_t3.append(delay[i])
                    elif timestamp_index == 4:
                        delay_corrections_v_array_t4.append(delay[i])
                    elif timestamp_index == 5:
                        delay_corrections_v_array_t5.append(delay[i])

        # Convert delays in seconds to 5th order polynomial coefficients
        # x is always [-25, -15, -5, 5, 15, 25] as the delays are calculated for the timestamps between
        # "t0 - 25" to "t0 + 25" at an interval of 10 seconds.
        x = np.array([-25, -15, -5, 5, 15, 25])
        for i in range(0, len(self.antenna_names)):
            antenna_delay_list = []
            antenna_delay_list.append(delay_corrections_h_array_t0[i])
            antenna_delay_list.append(delay_corrections_h_array_t1[i])
            antenna_delay_list.append(delay_corrections_h_array_t2[i])
            antenna_delay_list.append(delay_corrections_h_array_t3[i])
            antenna_delay_list.append(delay_corrections_h_array_t4[i])
            antenna_delay_list.append(delay_corrections_h_array_t5[i])

            # Array including delay values per antenna for the timestamps between "t0 - 25" to "t0 + 25"
            # at an interval of 10 seconds.
            y = np.array(antenna_delay_list)

            # Fit polynomial to the values over 50-second range
            polynomial = np.polynomial.Polynomial.fit(x, y, 5)
            polynomial_coefficients = polynomial.convert().coef
            delay_corrections_h_array_dict[self.antenna_names[i]] = polynomial_coefficients
        return delay_corrections_h_array_dict

    def update_config_params(self):
        """
        In this method parameters related to the resources assigned, are updated every time assign, release
        or configure commands are executed.

        :param argin: None

        :return: None

        """
        assigned_receptors_dict = {}
        assigned_receptors =[]

        # Load a set of antenna descriptions and construct Antenna objects from them
        with open(ska_antennas_path) as f:
            descriptions = f.readlines()
        antennas = [katpoint.Antenna(line) for line in descriptions]
        # Create a dictionary including antenna objects
        antennas_dict = {ant.name: ant for ant in antennas}
        antenna_keys_list = antennas_dict.keys()
        for receptor in self.receptorIDList_str:
            if receptor in antenna_keys_list:
                assigned_receptors.append(antennas_dict[receptor])
                # Create a dictionary including antennas (objects) assigned to the Subarray
                assigned_receptors_dict[receptor] = antennas_dict[receptor]

        # Antenna having key 'ref_ant' from antennas_dict, is referred as a reference antenna.
        ref_ant = antennas_dict["ref_ant"]

        # Create DelayCorrection Object
        self.delay_correction_object = katpoint.DelayCorrection(assigned_receptors, ref_ant)
        self.antenna_names = list(self.delay_correction_object.ant_models.keys())

        # list of frequency slice ids
        for fsp_entry in self.fsp_ids_object:
            self.fsids_list.append(fsp_entry["fspID"])

    def delay_model_calculator(self, argin):
        """
        This method calculates the delay model for consumption of CSP subarray.
        The epoch value is the current timestamp value. Delay calculation starts when configure
        command is invoked. It calls the function which internally calculates delay values using KATPoint
        library and converts them to fifth order polynomial coefficients.

        :param argin: int.
            The argument contains delay model update interval in seconds.

        :return: None.
        """
        delay_update_interval = argin

        # list of bands
        _bands_list = ["band1", "band2", "band3", "band4", "band5a", "band5b"]
        while not self._stop_delay_model_event.isSet():
            if(self.CspSubarrayProxy.obsState == CONST.ENUM_CONFIGURING
                    or self.CspSubarrayProxy.obsState == CONST.ENUM_READY
                    or self.CspSubarrayProxy.obsState == CONST.ENUM_SCANNING):
                self.logger.info("Calculating delays.")
                time_t0 = datetime.today() + timedelta(seconds=self._delay_in_advance)
                time_t0_utc = (time_t0.astimezone(pytz.UTC)).timestamp()

                delay_corrections_h_array_dict = self.calculate_geometric_delays(time_t0)
                delay_model_json = {}
                delay_model = []
                receptor_delay_model = []
                delay_model_per_epoch = {}
                for receptor in self.receptorIDList_str:
                    receptor_delay_object = {}
                    receptor_delay_object["receptor"] = receptor
                    receptor_specific_delay_details = []
                    for fsid in self.fsids_list:
                        fsid_delay_object = {}
                        fsid_delay_object["fsid"] = fsid
                        delay_coeff_array = []
                        receptor_delay_coeffs = delay_corrections_h_array_dict[receptor]
                        for i in range (0,len(receptor_delay_coeffs)):
                            delay_coeff_array.append(receptor_delay_coeffs[i])
                        fsid_delay_object["delayCoeff"] = delay_coeff_array
                        receptor_specific_delay_details.append(fsid_delay_object)
                    receptor_delay_object["receptorDelayDetails"] = receptor_specific_delay_details
                    receptor_delay_model.append(receptor_delay_object)
                delay_model_per_epoch["epoch"] = str(time_t0_utc)
                delay_model_per_epoch["delayDetails"] = receptor_delay_model
                delay_model.append(delay_model_per_epoch)
                delay_model_json["delayModel"] = delay_model
                print("delay_model_json: ", delay_model_json)
                log_msg = "delay_model_json: " + str(delay_model_json)
                self.logger.debug(log_msg)
                # update the attribute
                self.delay_model_lock.acquire()
                self._delay_model = json.dumps(delay_model_json)
                self.delay_model_lock.release()

                # wait for timer event
                self._stop_delay_model_event.wait(delay_update_interval)
            else:
                self._delay_model = " "

        self.logger.debug("Stop event received. Thread exit.")

    # Function for handling all Devfailed exception
    def _handle_devfailed_exception(self, df, except_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(df)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(df)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    # Function for handling all generic exception
    def _handle_generic_exception(self, exception, except_msg_list, exception_count,read_actvity_msg ):
        log_msg = read_actvity_msg + str(exception)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(exception)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    def throw_exception(self, except_msg_list, read_actvity_msg):
        err_msg = ''
        for item in except_msg_list:
            err_msg += item + "\n"
        tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)

    def init_device(self):
        """
        Initializes the attributes and properties of the CspSubarrayLeafNode.
        """
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CspSubarrayLeafNode.init_device) ENABLED START #

        try:
            self._state = 0
            try:
                # create CspSubarray Proxy
                self.CspSubarrayProxy = DeviceProxy(self.CspSubarrayFQDN)
            except Exception:
                self.logger.debug(CONST.ERR_IN_CREATE_PROXY_CSPSA)

            # create CspSubarray Proxy
            # self.CspSubarrayProxy = DeviceProxy(self.CspSubarrayFQDN)
            self._read_activity_message = " "
            self._delay_model = " "
            self._visdestination_address = " "
            self._versioninfo = " "
            self.receptorIDList = []
            self.fsp_ids_object =[]
            self.fsids_list = []
            self.target_Ra = ""
            self.target_Dec = ""

            ## Start thread to update delay model ##
            # Create event
            self._stop_delay_model_event = threading.Event()
            #
            # create lock
            self.delay_model_lock = threading.Lock()

            # create thread
            self.logger.debug("Starting thread to calculate delay model.")
            self.delay_model_calculator_thread = threading.Thread(
                target=self.delay_model_calculator,
                args=[self._DELAY_UPDATE_INTERVAL],
                daemon=False)
            self.delay_model_calculator_thread.start()
            self.set_state(DevState.ON)
            self.set_status(CONST.STR_CSPSALN_INIT_SUCCESS)
            self._csp_subarray_health_state = CONST.ENUM_OK
            self.logger.info(CONST.STR_CSPSALN_INIT_SUCCESS)

        except DevFailed as dev_failed:
            self._handle_devfailed_exception(dev_failed, CONST.ERR_INIT_PROP_ATTR_CSPSALN, 0,
                                                                CONST.STR_ERR_MSG)
            self.logger.debug(CONST.ERR_INIT_PROP_ATTR_CSPSALN)
            self.logger.debug(CONST.STR_ERR_MSG, dev_failed)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # Stop thread to update delay model
        self.logger.debug("Stopping delay model thread.")
        self._stop_delay_model_event.set()
        self.delay_model_calculator_thread.join()
        self.logger.debug("Exiting.")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_state(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.state_read) ENABLED START #
        '''Internal construct of TANGO. Returns the state of device.'''
        return self._state
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.state_read

    def read_delayModel(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_read) ENABLED START #
        '''Internal construct of TANGO. Returns the delay model.'''
        return self._delay_model
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_read

    def write_delayModel(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_write) ENABLED START #
        '''Internal construct of TANGO. Sets in to the delay model.'''
        self._delay_model = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_write

    def read_visDestinationAddress(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_read) ENABLED START #
        '''Internal construct of TANGO. Returns the destination address.'''
        return self._visdestination_address
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_read

    def write_visDestinationAddress(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_write) ENABLED START #
        '''Internal construct of TANGO. Sets the destination address.'''
        self._visdestination_address = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_write

    def read_versionInfo(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.versionInfo_read) ENABLED START #
        '''Internal construct of TANGO. Returns the version information.'''
        return self._versioninfo
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_read) ENABLED START #
        '''Internal construct of TANGO. Returns activity message.'''
        return self._read_activity_message
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_write) ENABLED START #
        '''Internal construct of TANGO. Sets the activity message.'''
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_write


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

        {"frequencyBand":"1","fsp":[{"fspID":1,"functionMode":"CORR","frequencySliceID":1,
        "integrationTime":1400,"corrBandwidth":0}],"delayModelSubscriptionPoint":
        "ska_mid/tm_leaf_node/csp_subarray01/delayModel","visDestinationAddressSubscriptionPoint":
        "mid_sdp/elt/subarray_1/receiveAddresses","pointing":{"target":{"system":"ICRS","name":"Polaris",
        "RA":"20:21:10.31","dec":"-30:52:17.3"}},"scanID":"123"}


        :return: None.
        """
        exception_message = []
        exception_count = 0
        try:
            print("argin configure: ", argin)
            argin_json = json.loads(argin)
            # Used to extract FSP IDs
            self.fsp_ids_object = argin_json["fsp"]
            self.update_config_params()
            self.pointing_params = argin_json["pointing"]
            self.target_Ra = self.pointing_params["target"]["RA"]
            self.target_Dec = self.pointing_params["target"]["dec"]
            # Create target object
            self.target = katpoint.Target('radec , ' + str(self.target_Ra) + ", " + str(self.target_Dec))

            cspConfiguration = argin_json.copy()
            # Keep configuration specific to CSP and delete pointing configuration
            if "pointing" in cspConfiguration:
                del cspConfiguration["pointing"]

            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevString, json.dumps(cspConfiguration))

            self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_CONFIGURESCAN, cmdData,
                                                       self.commandCallback)
            self._read_activity_message = CONST.STR_CONFIGURESCAN_SUCCESS
            self.logger.info(CONST.STR_CONFIGURESCAN_SUCCESS)
            self.logger.debug(argin)

        except ValueError as value_error:
            log_msg = CONST.ERR_INVALID_JSON_CONFIG_SCAN + str(value_error)
            self.logger.error(log_msg)
            self._read_activity_message = CONST.ERR_INVALID_JSON_CONFIG_SCAN + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        except DevFailed as dev_failed:
            [exception_count,exception_message] = self._handle_devfailed_exception(dev_failed,
                                exception_message, exception_count, CONST.ERR_CONFIGURESCAN_INVOKING_CMD)

        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception( except_occurred,
                                    exception_message, exception_count, CONST.ERR_CONFIGURESCAN_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_CONFIG_SCAN_EXEC)

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
        exception_message = []
        exception_count = 0
        try:
            json_scan_duration = json.loads(argin[0])
            scan_duration = json_scan_duration["scanDuration"]
            #Check if CspSubarray is in READY state
            if self.CspSubarrayProxy.obsState == CONST.ENUM_READY:
                #Invoke StartScan command on CspSubarray
                self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_STARTSCAN, "0", self.commandCallback)
                self._read_activity_message = CONST.STR_STARTSCAN_SUCCESS
                self.logger.info(CONST.STR_STARTSCAN_SUCCESS)
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_READY
                self.logger.error(CONST.ERR_DEVICE_NOT_READY)

        except DevFailed as dev_failed:
            [exception_count, exception_message] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count, CONST.ERR_STARTSCAN_RESOURCES)

        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception(except_occurred,
                                        exception_message, exception_count, CONST.ERR_STARTSCAN_RESOURCES)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_START_SCAN_EXEC)

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
        exception_message = []
        exception_count = 0
        try:
            if self.CspSubarrayProxy.obsState == CONST.ENUM_SCANNING:
                # Invoke EndScan command on CspSubarray
                self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_ENDSCAN, self.commandCallback)
                self._read_activity_message = CONST.STR_ENDSCAN_SUCCESS
                self.logger.info(CONST.STR_ENDSCAN_SUCCESS)
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_IN_SCAN
                self.logger.error(CONST.ERR_DEVICE_NOT_IN_SCAN)

        except DevFailed as dev_failed:
            [exception_count, exception_message] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count, CONST.ERR_ENDSCAN_INVOKING_CMD)

        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception(except_occurred,
                                        exception_message, exception_count, CONST.ERR_ENDSCAN_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_ENDSCAN_EXEC)

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
        exception_message = []
        exception_count = 0
        try:
            #Invoke RemoveAllReceptors command on CspSubarray
            self.receptorIDList = []
            self.fsids_list = []
            self.update_config_params()
            self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_REMOVE_ALL_RECEPTORS, self.commandCallback)
            self._read_activity_message = CONST.STR_REMOVE_ALL_RECEPTORS_SUCCESS
            self.logger.info(CONST.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

        except DevFailed as dev_failed:
            [exception_count, exception_message] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count, CONST.ERR_RELEASE_ALL_RESOURCES)
        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception(except_occurred,
                                        exception_message, exception_count, CONST.ERR_RELEASE_ALL_RESOURCES)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_RELEASE_RES_EXEC)

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
                    DevVarString
                    The individual string should contain dish numbers in string format
                    with preceding zeroes upto 3 digits. E.g. 0001, 0002.
        Example:
                {
                "subarrayID": 1,
                "dish": {
                "receptorIDList": ["0001", "0002"]
                }
                }

         Note: Enter input without spaces as:{"subarrayID":1,"dish":{"receptorIDList":["0001","0002"]}}
        :return: None.
        """
        exception_message = []
        exception_count = 0
        try:
            #Parse receptorIDList from JSON string.
            jsonArgument = json.loads(argin[0])
            self.receptorIDList_str = jsonArgument[CONST.STR_DISH][CONST.STR_RECEPTORID_LIST]
            #convert receptorIDList from list of string to list of int
            for i in range(0, len(self.receptorIDList_str)):
                self.receptorIDList.append(int(self.receptorIDList_str[i]))
            self.update_config_params()

            #Invoke AddReceptors command on CspSubarray
            self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_ADD_RECEPTORS, self.receptorIDList,
                                                       self.commandCallback)

            self._read_activity_message = CONST.STR_ADD_RECEPTORS_SUCCESS
            self.logger.info(CONST.STR_ADD_RECEPTORS_SUCCESS)

        except ValueError as value_error:
            log_msg = CONST.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
            self.logger.error(log_msg)
            self._read_activity_message = CONST.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        except KeyError as key_error:
            log_msg = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.error(log_msg)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        except DevFailed as dev_failed:
            [exception_count, exception_message] = self._handle_devfailed_exception(dev_failed,
                                         exception_message, exception_count, CONST.ERR_ASSGN_RESOURCES)

        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception(except_occurred,
                                         exception_message, exception_count, CONST.ERR_ASSGN_RESOURCES)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_ASSIGN_RES_EXEC)

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
        exception_message = []
        exception_count = 0
        try:
            if self.CspSubarrayProxy.obsState == CONST.ENUM_READY:
                self.CspSubarrayProxy.command_inout_asynch(CONST.CMD_ENDSB, self.commandCallback)
                self._read_activity_message = CONST.STR_ENDSB_SUCCESS
                self.logger.info(CONST.STR_ENDSB_SUCCESS)
            else:
                self._read_activity_message = CONST.ERR_DEVICE_NOT_READY
                self.logger.error(CONST.ERR_DEVICE_NOT_READY)
        except DevFailed as dev_failed:
            [exception_count, exception_message] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, CONST.ERR_ENDSB_INVOKING_CMD)

        except Exception as except_occurred:
            [exception_count, exception_message] = self._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, CONST.ERR_ENDSB_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, CONST.STR_ENDSB_EXEC)

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
