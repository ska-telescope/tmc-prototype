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
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PROTECTED REGION ID(CspSubarrayLeafNode.additional_import) ENABLED START #
# Standard python imports
import datetime
import importlib.resources
import threading
from datetime import datetime, timedelta
import pytz
import numpy as np
import json

# Third Party imports
# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, DevState, DevFailed
from tango.server import run, attribute, command, device_property
import katpoint

# Additional import
from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState
from . import const, release
from .exceptions import InvalidObsStateError
# PROTECTED REGION END #    //  CspSubarrayLeafNode.additional_import

__all__ = ["CspSubarrayLeafNode", "main"]


class CspSubarrayLeafNode(SKABaseDevice):
    """
    CSP Subarray Leaf node monitors the CSP Subarray and issues control actions during an observation.
    """
    # PROTECTED REGION ID(CspSubarrayLeafNode.class_variable) ENABLED START #

    _DELAY_UPDATE_INTERVAL = 10
    # _delay_in_advance variable (in seconds) is added to current timestamp and is used to calculate advance
    # delay coefficients.
    _delay_in_advance = 60

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
    delayModel = attribute(
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
        assigned_receptors = []

        self.logger.info("Updating config parameters.")

        # Load a set of antenna descriptions and construct Antenna objects from them
        with importlib.resources.open_text("cspsubarrayleafnode", "ska_antennas.txt") as f:
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

        while not self._stop_delay_model_event.isSet():
            if self._csp_subarray_proxy.obsState in (ObsState.CONFIGURING, ObsState.READY, ObsState.SCANNING):
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
                        for i in range(0, len(receptor_delay_coeffs)):
                            delay_coeff_array.append(receptor_delay_coeffs[i])
                        fsid_delay_object["delayCoeff"] = delay_coeff_array
                        receptor_specific_delay_details.append(fsid_delay_object)
                    receptor_delay_object["receptorDelayDetails"] = receptor_specific_delay_details
                    receptor_delay_model.append(receptor_delay_object)
                delay_model_per_epoch["epoch"] = str(time_t0_utc)
                delay_model_per_epoch["delayDetails"] = receptor_delay_model
                delay_model.append(delay_model_per_epoch)
                delay_model_json["delayModel"] = delay_model
                log_msg = "delay_model_json: " + str(delay_model_json)
                self.logger.debug(log_msg)
                # update the attribute
                self.delay_model_lock.acquire()
                self._delay_model = json.dumps(delay_model_json)
                self.delay_model_lock.release()

                # wait for timer event
                self._stop_delay_model_event.wait(delay_update_interval)
            else:
                # TODO: This waiting on event is added temporarily to reduce high CPU usage.
                self._stop_delay_model_event.wait(0.02)
                self._delay_model = " "

        self.logger.debug("Stop event received. Thread exit.")


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
            try:
                # create CspSubarray Proxy
                device._csp_subarray_proxy = DeviceProxy(device.CspSubarrayFQDN)
            except DevFailed as dev_failed:
                log_msg = const.ERR_IN_CREATE_PROXY_CSPSA + str(dev_failed)
                self.logger.debug(log_msg)
                return (ResultCode.FAILED, log_msg)
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._read_activity_message = " "
            device._delay_model = " "
            device._versioninfo = " "
            device.receptorIDList_str = []
            device.fsp_ids_object = []
            device.fsids_list = []
            ## Start thread to update delay model ##
            # Start thread to update delay model
            # Create event
            device._stop_delay_model_event = threading.Event()

            # create lock
            device.delay_model_lock = threading.Lock()

            # create thread
            self.logger.debug("Starting thread to calculate delay model.")
            device.delay_model_calculator_thread = threading.Thread(
                target=device.delay_model_calculator,
                args=[device._DELAY_UPDATE_INTERVAL],
                daemon=False)
            device.delay_model_calculator_thread.start()
            device.set_status(const.STR_CSPSALN_INIT_SUCCESS)
            device._csp_subarray_health_state = HealthState.OK
            self.logger.info(const.STR_CSPSALN_INIT_SUCCESS)
            return (ResultCode.OK, const.STR_CSPSALN_INIT_SUCCESS)

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
    class ConfigureCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's Configure() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
                current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Configure() is not allowed in current state",
                                             "Failed to invoke Configure command on cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.Configure()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState not in [ObsState.IDLE, ObsState.READY]:
                tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY_OR_IDLE, const.ERR_CONFIGURE_INVOKING_CMD,
                                             "CspSubarrayLeafNode.ConfigureCommand",
                                             tango.ErrSeverity.ERR)
            return True

        def configure_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self, argin):
            """
            This command configures a scan. It accepts configuration information in JSON string format and
            invokes Configure command on CspSubarray.

            :param argin:DevString. The string in JSON format. The JSON contains following values:

            Example:
            {"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","fsp":[{"fspID":1,"functionMode":
            "CORR", "frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":
            [[0,2],[744,0]], "fspChannelOffset":0,"outputLinkMap":[[0,0],[200,1]],"outputHost":[[0,
            "192.168.1.1"]],"outputPort": [[0,9000,1]]},{"fspID":2,"functionMode":"CORR","frequencySliceID":2,
            "integrationTime":1400,"corrBandwidth":0, "channelAveragingMap":[[0,2],[744,0]],
             "fspChannelOffset":744,"outputLinkMap":[[0,4],[200,5]],"outputHost": [[0,"192.168.1.1"]],
             "outputPort":[[0,9744,1]]}],"delayModelSubscriptionPoint":
            "ska_mid/tm_leaf_node/csp_subarray01/delayModel","pointing":{"target":{"system":"ICRS",
            "name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}}}

            Note: Enter the json string without spaces as a input.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the command execution is not successful
                     ValueError if input argument json string contains invalid value
            """
            device = self.target
            target_Ra = ""
            target_Dec = ""
            try:
                argin_json = json.loads(argin)
                # Used to extract FSP IDs
                device.fsp_ids_object = argin_json["fsp"]
                device.update_config_params()
                pointing_params = argin_json["pointing"]
                target_Ra = pointing_params["target"]["RA"]
                target_Dec = pointing_params["target"]["dec"]

                # Create target object
                device.target = katpoint.Target('radec , ' + str(target_Ra) + ", " + str(target_Dec))
                cspConfiguration = argin_json.copy()
                cspConfiguration = argin_json.copy()
                # Keep configuration specific to CSP and delete pointing configuration
                if "pointing" in cspConfiguration:
                    del cspConfiguration["pointing"]
                log_msg = "Input JSON for CSP Subarray Leaf Node Configure command is: " + argin
                self.logger.debug(log_msg)
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_CONFIGURE, json.dumps(cspConfiguration),
                                                           self.configure_cmd_ended_cb)
                device._read_activity_message = const.STR_CONFIGURE_SUCCESS
                self.logger.info(const.STR_CONFIGURE_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_CONFIG + str(value_error)
                device._read_activity_message = log_msg
                self.logger.exception(value_error)
                tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                             "CspSubarrayLeafNode.ConfigureCommand",
                                             tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_CONFIGURE_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_CONFIGURE_INVOKING_CMD, log_msg,
                                             "CspSubarrayLeafNode.ConfigureCommand",
                                             tango.ErrSeverity.ERR)

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
        dtype_in=('str'),
        doc_in="The string in JSON format, contains CSP configuration id, frequencyBand, fsp,"
               " delayModelSubscriptionPoint and pointing information.",
    )
    @DebugIt()
    def Configure(self, argin):
        """ Invokes Configure command on CspSubarrayLeafNode """
        handler = self.get_command_object("Configure")
        handler(argin)

    class StartScanCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's StartScan() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
                current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("StartScan() is not allowed in current state",
                                             "Failed to invoke StartScan command on cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.StartScan()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState != ObsState.READY:
                tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY, const.STR_OBS_STATE,
                                             "CspSubarrayLeafNode.StartScanCommand",
                                             tango.ErrSeverity.ERR)

            return True

        def startscan_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            # TODO: This code does not generate exception so refactoring is required
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self, argin):
            """
            This command invokes Scan command on CspSubarray. It is allowed only when CspSubarray is in
            ObsState READY.

            :param argin: JSON string consists of scan id (int).

            Example:
            {"id":1}

            Note: Enter the json string without spaces as a input.

            :return: A tuple containing a return code and a string message indicating status.
             The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_STARTSCAN, "0",
                                                             self.startscan_cmd_ended_cb)
                device._read_activity_message = const.STR_STARTSCAN_SUCCESS
                self.logger.info(const.STR_STARTSCAN_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_STARTSCAN_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_START_SCAN_EXEC, log_msg,
                                             "CspSubarrayLeafNode.StartScanCommand",
                                             tango.ErrSeverity.ERR)

    @command(
        dtype_in=('str',),
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

    class EndScanCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's EndScan() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
            current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
            in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("EndScan() is not allowed in current state",
                                             "Failed to invoke EndScan command on cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.EndScan()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState != ObsState.SCANNING:
                tango.Except.throw_exception(const.ERR_DEVICE_NOT_IN_SCAN, "Failed to invoke EndScan command on cspsubarrayleafnode.",
                                             "CspSubarrayLeafNode.EndScanCommand",
                                             tango.ErrSeverity.ERR)

            return True

        def endscan_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            It invokes EndScan command on CspSubarray. This command is allowed when CspSubarray is in
            obsState SCANNING

            :return: A tuple containing a return code and a string message indicating status.
                    The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_ENDSCAN, self.endscan_cmd_ended_cb)
                device._read_activity_message = const.STR_ENDSCAN_SUCCESS
                self.logger.info(const.STR_ENDSCAN_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ENDSCAN_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_ENDSCAN_EXEC, log_msg,
                                             "CspSubarrayLeafNode.EndScanCommand",
                                             tango.ErrSeverity.ERR)

    def is_EndScan_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    @command(
    )
    @DebugIt()
    def EndScan(self):
        """ Invokes EndScan command on CspSubarrayLeafNode"""
        handler = self.get_command_object("EndScan")
        handler()

    class ReleaseAllResourcesCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's ReleaseAllResources() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("ReleaseAllResources() is not allowed in current state",
                                             "Failed to invoke ReleaseAllResources command on "
                                             "cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.ReleaseAllResources()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState != ObsState.IDLE:
                tango.Except.throw_exception(const.ERR_DEVICE_NOT_IDLE, "Failed to invoke ReleaseAllResourcesCommand command on cspsubarrayleafnode.",
                                             "CspSubarrayLeafNode.ReleaseAllResourcesCommand",
                                             tango.ErrSeverity.ERR)

            return True

        def releaseallresources_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            It invokes RemoveAllReceptors command on CspSubarray and releases all the resources assigned to
            CspSubarray.

            :return: None

            :raises: DevFailed if the command execution is not successful

            """
            device = self.target
            try:
                # Invoke RemoveAllReceptors command on CspSubarray
                device.receptorIDList = []
                device.fsids_list = []
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_REMOVE_ALL_RECEPTORS,
                                                             self.releaseallresources_cmd_ended_cb)
                device._read_activity_message = const.STR_REMOVE_ALL_RECEPTORS_SUCCESS
                self.logger.info(const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_RELEASE_ALL_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                             "CspSubarrayLeafNode.ReleaseAllResourcesCommand",
                                             tango.ErrSeverity.ERR)

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

    @command(
    )
    @DebugIt()
    def ReleaseAllResources(self):
        """ Invokes ReleaseAllResources command on CspSubarrayLeafNode"""
        handler = self.get_command_object("ReleaseAllResources")
        handler()

    class AssignResourcesCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's AssignResources() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("AssignResources() is not allowed in current state",
                                             "Failed to invoke AssignResources command on "
                                             "cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.AssignResources()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState not in ObsState.EMPTY :
                tango.Except.throw_exception("AssignResources() is not allowed in current state", "Failed to invoke AssignResources command.",
                                             "CspSubarrayLeafNode.AssignResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def add_receptors_ended(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none

            :raises: DevFailed if this command is not allowed to be run
            in current device state

            """
            device = self.target
            self.logger.info("Executing callback add_receptors_ended")
            try:
                if event.err:
                    device._read_activity_message = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                        event.errors)
                    log = const.ERR_INVOKING_CMD + event.cmd_name
                    self.logger.error(log)
                else:
                    log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                    device._read_activity_message = log
                    self.logger.info(log)

            except tango.DevFailed as df:
                self.logger.exception(df)
                tango.Except.re_throw_exception(df, "CSP subarray gave an error response",
                                                "CSP subarray threw error in AddReceptors CSP LMC_CommandFailed",
                                                "AddReceptors", tango.ErrSeverity.ERR)

        def do(self, argin):
            """
            It accepts receptor id list in JSON string format and invokes AddReceptors command on CspSubarray
            with receptorIDList (list of integers) as an input argument.

            :param argin:DevString. The string in JSON format. The JSON contains following values:

                dish:
                    Mandatory JSON object consisting of

                    receptorIDList:
                        DevVarString
                        The individual string should contain dish numbers in string format
                        with preceding zeroes upto 3 digits. E.g. 0001, 0002.
            Example:
            {
              "dish": {
                "receptorIDList": [
                  "0001",
                  "0002"
                ]
              }
            }

            Note: Enter the json string without spaces as an input.

            :return: None

            :raises: ValueError if input argument json string contains invalid value
                     KeyError if input argument json string contains invalid key
                     DevFailed if the command execution is not successful
            """
            device = self.target
            receptorIDList = []
            try:
                # Parse receptorIDList from JSON string.
                json_argument = json.loads(argin)
                device.receptorIDList_str = json_argument[const.STR_DISH][const.STR_RECEPTORID_LIST]
                # convert receptorIDList from list of string to list of int
                for receptor in device.receptorIDList_str:
                    receptorIDList.append(int(receptor))
                self.logger.info("receptorIDList: %s", str(receptorIDList))
                device.update_config_params()
                # Invoke AddReceptors command on CspSubarray
                self.logger.info("Invoking AddReceptors on CSP subarray")

                device._csp_subarray_proxy.command_inout_asynch(const.CMD_ADD_RECEPTORS, receptorIDList,
                                                           self.add_receptors_ended)

                self.logger.info("After invoking AddReceptors on CSP subarray")
                device._read_activity_message = const.STR_ADD_RECEPTORS_SUCCESS
                self.logger.info(const.STR_ADD_RECEPTORS_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
                device._read_activity_message = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
                self.logger.exception(value_error)
                tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "CspSubarrayLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except KeyError as key_error:
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                self.logger.exception(key_error)
                tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "CspSubarrayLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "CspSubarrayLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)

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
        dtype_in=('str'),
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
            tango.Except.throw_exception("ObsState is not in EMPTY state",
                                         "CSP subarray leaf node raised exception",
                                         "CSP.AddReceptors",
                                         tango.ErrSeverity.ERR)
        handler(argin)

    class GoToIdleCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's GoToIdle() command.
        """

        def check_allowed(self):
            """
            Checks whether the command is allowed to be run in the current state

            :return: True if this command is allowed to be run in
                current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run
                in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("GoToIdle() is not allowed in current state",
                                             "Failed to invoke GoToIdle command on cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.GoToIdle()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState != ObsState.READY:
                tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY, "Failed to invoke GoToIdle command on cspsubarrayleafnode.",
                                             "CspSubarrayLeafNode.GoToIdleCommand",
                                             tango.ErrSeverity.ERR)
            return True

        def gotoidle_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            This command invokes GoToIdle command on CSP Subarray in order to end current scheduling block.

            :return: None

            :raises: DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_GOTOIDLE, self.gotoidle_cmd_ended_cb)
                device._read_activity_message = const.STR_GOTOIDLE_SUCCESS
                self.logger.info(const.STR_GOTOIDLE_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_GOTOIDLE_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_GOTOIDLE_INVOKING_CMD, log_msg,
                                             "CspSubarrayLeafNode.GoToIdleCommand",
                                             tango.ErrSeverity.ERR)

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

    @command(
    )
    @DebugIt()
    def GoToIdle(self):
        """ Invokes GoToIdle command on CspSubarrayLeafNode. """
        handler = self.get_command_object("GoToIdle")
        handler()

    def validate_obs_state(self):
        if self._csp_subarray_proxy.obsState == ObsState.EMPTY:
            self.logger.info("CSP Subarray is in required obsState, resources will be assigned")
        else:
            self.logger.error("CSP Subarray is not in EMPTY obsState")
            self._read_activity_message = "Error in device obsState"
            raise InvalidObsStateError("CSP Subarray is not in EMPTY obsState")

    class AbortCommand(BaseCommand):
        """
        A class for CSPSubarrayLeafNode's Abort() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Abort() is not allowed in current state",
                                             "Failed to invoke Abort command on CspSubarrayLeafNode.",
                                             "cspsubarrayleafnode.Abort()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState not in [ObsState.READY, ObsState.CONFIGURING, ObsState.SCANNING,
                                                            ObsState.IDLE, ObsState.RESETTING]:
                tango.Except.throw_exception(const.ERR_UNABLE_ABORT_CMD, const.ERR_ABORT_INVOKING_CMD,
                                         "CspSubarrayLeafNode.AbortCommand",
                                         tango.ErrSeverity.ERR)

            return True

        def abort_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            This command invokes Abort command on CSP Subarray.

            :return: None

            :raises: DevFailed if error occurs while invoking command on CSPSubarray.

            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_ABORT, self.abort_cmd_ended_cb)
                device._read_activity_message = const.STR_ABORT_SUCCESS
                self.logger.info(const.STR_ABORT_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ABORT_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_ABORT_EXEC, log_msg,
                                             "CspSubarrayLeafNode.AbortCommand",
                                             tango.ErrSeverity.ERR)

    @command(
    )
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

    class RestartCommand(BaseCommand):
        """
        A class for CSPSubarrayLeafNode's Restart() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Restart() is not allowed in current state",
                                             "Failed to invoke Restart command on CspSubarrayLeafNode.",
                                             "cspsubarrayleafnode.Restart()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState not in [ObsState.FAULT, ObsState.ABORTED]:
                tango.Except.throw_exception(const.ERR_UNABLE_RESTART_CMD, const.ERR_RESTART_INVOKING_CMD,
                                             "CspSubarrayLeafNode.RestartCommand",
                                             tango.ErrSeverity.ERR)

            return True


        def restart_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            This command invokes Restart command on CSPSubarray.

            :return: None

            :raises: DevFailed if error occurs while invoking the command on CSpSubarray.
            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_RESTART, self.restart_cmd_ended_cb)
                device._read_activity_message = const.STR_RESTART_SUCCESS
                self.logger.info(const.STR_RESTART_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_RESTART_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_RESTART_INVOKING_CMD, log_msg,
                                             "CspSubarrayLeafNode.RestartCommand",
                                             tango.ErrSeverity.ERR)

    @command(
    )
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

    class ObsResetCommand(BaseCommand):
        """
        A class for CSPSubarrayLeafNode's ObsReset() command.
        """
        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
                log_msg= "ObsReset() is not allowed in " + str(self.state_model.op_state)
                tango.Except.throw_exception(log_msg ,
                                             "Failed to invoke ObsReset command on CspSubarrayLeafNode.",
                                             "cspsubarrayleafnode.ObsReset()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState not in [ObsState.ABORTED, ObsState.FAULT]:
                tango.Except.throw_exception(const.ERR_UNABLE_OBSRESET_CMD, const.ERR_OBSRESET_INVOKING_CMD,
                                             "CspSubarrayLeafNode.ObsResetCommand",
                                             tango.ErrSeverity.ERR)

            return True

        def obsreset_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns. 

            :param event: a CmdDoneEvent object. This class is used to pass data
                to the callback method in asynchronous callback model for command
                execution.

            :type: CmdDoneEvent object
                It has the following members:
                    - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                    - cmd_name   : (str) The command name
                    - argout_raw : (DeviceData) The command argout
                    - argout     : The command argout
                    - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                    - errors     : (sequence<DevError>) The error stack
                    - ext

            :return: none
            """
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            Command to reset the CSP subarray and bring it to its RESETTING state.

            :param argin: None

            :return: None

            :raises: DevFailed if error occurs while invoking the command on CSpSubarray.
            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_OBSRESET, self.obsreset_cmd_ended_cb)
                device._read_activity_message = const.STR_OBSRESET_SUCCESS
                self.logger.info(const.STR_OBSRESET_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(log_msg)
                tango.Except.throw_exception(const.ERR_OBSRESET_INVOKING_CMD, log_msg,
                                             "CspSubarrayLeafNode.ObsResetCommand",
                                             tango.ErrSeverity.ERR)
        
    @command(
    )
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
        args = (self, self.state_model, self.logger)
        self.register_command_object("AssignResources", self.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseAllResources", self.ReleaseAllResourcesCommand(*args))
        self.register_command_object("Configure", self.ConfigureCommand(*args))
        self.register_command_object("StartScan", self.StartScanCommand(*args))
        self.register_command_object("EndScan", self.EndScanCommand(*args))
        self.register_command_object("GoToIdle", self.GoToIdleCommand(*args))
        self.register_command_object("Abort", self.AbortCommand(*args))
        self.register_command_object("Restart", self.RestartCommand(*args))
        self.register_command_object("ObsReset", self.ObsResetCommand(*args))


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
