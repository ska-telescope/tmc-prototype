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
import datetime
import importlib.resources
import threading
from datetime import datetime, timedelta
import pytz
import katpoint
import numpy as np

# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, DevState, DevFailed

from ska.base.commands import ResultCode, ResponseCommand
from tango.server import run,attribute, command, device_property
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState

# Additional import
# PROTECTED REGION ID(CspSubarrayLeafNode.additionnal_import) ENABLED START #
import json
from . import const
# PROTECTED REGION END #    //  CspSubarrayLeafNode.additionnal_import

__all__ = ["CspSubarrayLeafNode", "main"]

# pylint: disable=protected-access,unused-argument,unused-variable
class CspSubarrayLeafNode(SKABaseDevice):
    """
    CSP Subarray Leaf node monitors the CSP Subarray and issues control actions during an observation.
    """
    # PROTECTED REGION ID(CspSubarrayLeafNode.class_variable) ENABLED START #

    _DELAY_UPDATE_INTERVAL = 10
    # _delay_in_advance variable (in seconds) is added to current timestamp and is used to calculate advance
    # delay coefficients.
    _delay_in_advance = 60
    # _stop_delay_model_event = # type: Event

    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on CspSubarray.

        :param event: a CmdDoneEvent object. This class is used to pass data
            to the callback method in asynchronous callback model for command
            execution.
        :type: CmdDoneEvent object
            It has the following members:
                - device     : (DeviceProxy) The DeviceProxy object on which the
                               call was executed.
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to true if the command
                               failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext
        :return: none
        """
        exception_count = 0
        exception_message = []
        # Update logs and activity message attribute with received event
        try:
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                self._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                self._read_activity_message = log_msg
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, const.ERR_EXCEPT_CMD_CB)

        # Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_CMD_CALLBK)

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
    # state = attribute(
    #     dtype='DevEnum',
    #     enum_labels=["INIT", "ON", "ALARM", "FAULT", "UNKNOWN", "DISABLE", ],
    # )

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
        assigned_receptors =[]

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
            if(self.CspSubarrayProxy.obsState == ObsState.CONFIGURING
                    or self.CspSubarrayProxy.obsState == ObsState.READY
                    or self.CspSubarrayProxy.obsState == ObsState.SCANNING):
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
        tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg, read_actvity_msg, tango.ErrSeverity.ERR)

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the CspSubarrayLeafNode's init_device() "command".
        """
        # PROTECTED REGION ID(CspSubarrayLeafNode.init_device) ENABLED START #
        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ReturnCode, str)
            """
            super().do()
            device=self.target
            try:
                # create CspSubarray Proxy
                device.CspSubarrayProxy = DeviceProxy(device.CspSubarrayFQDN)
            except Exception:
                log_msg = const.ERR_IN_CREATE_PROXY_CSPSA + str(Exception)
                self.logger.debug(log_msg)
                return (ResultCode.FAILED,log_msg)

            # create CspSubarray Proxy
            # self.CspSubarrayProxy = DeviceProxy(self.CspSubarrayFQDN)
            device._read_activity_message = " "
            device._delay_model = " "
            device._versioninfo = " "
            device.receptorIDList = []
            device.fsp_ids_object =[]
            device.fsids_list = []
            device.target_Ra = ""
            device.target_Dec = ""
            ## Start thread to update delay model ##
            # Create event
            device._stop_delay_model_event = threading.Event()
            #
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
            return (ResultCode.OK,const.STR_CSPSALN_INIT_SUCCESS)

            # except DevFailed as dev_failed:
            #     device._handle_devfailed_exception(dev_failed, const.ERR_INIT_PROP_ATTR_CSPSALN, 0,
            #                                                         const.STR_ERR_MSG)
            #     self.logger.debug(const.ERR_INIT_PROP_ATTR_CSPSALN)
            #     self.logger.debug(const.STR_ERR_MSG,dev_failed)

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
        self.logger.debug("CSP Subarray Leaf Node is Exiting.")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delete_device

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        self.register_command_object(
            "AssignResources",
            self.AssignResourcesCommand(self, self.state_model, self.logger)
        )
        self.register_command_object(
            "ReleaseAllResources",
            self.ReleaseAllResourcesCommand(self, self.state_model, self.logger)
        )
        self.register_command_object(
            "Configure",
            self.ConfigureCommand(self, self.state_model, self.logger)
        )
        self.register_command_object(
            "StartScan",
            self.StartScanCommand(self, self.state_model, self.logger)
        )
        self.register_command_object(
            "EndScan",
            self.EndScanCommand(self, self.state_model, self.logger)
        )
        self.register_command_object(
            "GoToIdle",
            self.GoToIdleCommand(self, self.state_model, self.logger)
        )

    # ------------------
    # Attributes methods
    # ------------------

    # def read_state(self):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.state_read) ENABLED START #
    #     '''Internal construct of TANGO. Returns the state of device.'''
    #     return self._state
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.state_read

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
# -------------------------------------------------------------------------------------------------------

    # @command(
    #     dtype_in='str',
    # )
    # @DebugIt()
    # def Configure(self, argin):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.Configure) ENABLED START #
    #     """
    #     This command configures the scan. It accepts configuration capabilities in JSON string format and
    #     invokes Configure command on CspSubarray with configuration capabilities in JSON string as an
    #     input argument.
    #
    #     :param argin: The string in JSON format. The JSON contains following values:
    #
    #     Example:
    #     {"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","fsp":[{"fspID":1,"functionMode":"CORR",
    #     "frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[[0,2],[744,0]],
    #     "fspChannelOffset":0,"outputLinkMap":[[0,0],[200,1]],"outputHost":[[0,"192.168.1.1"]],"outputPort":
    #     [[0,9000,1]]},{"fspID":2,"functionMode":"CORR","frequencySliceID":2,"integrationTime":1400,"corrBandwidth":0,
    #     "channelAveragingMap":[[0,2],[744,0]],"fspChannelOffset":744,"outputLinkMap":[[0,4],[200,5]],"outputHost":
    #     [[0,"192.168.1.1"]],"outputPort":[[0,9744,1]]}],"delayModelSubscriptionPoint":
    #     "ska_mid/tm_leaf_node/csp_subarray01/delayModel","pointing":{"target":{"system":"ICRS",
    #     "name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}}}
    #
    #     :return: None.
    #     """
    #     exception_message = []
    #     exception_count = 0
    #     try:
    #         argin_json = json.loads(argin)
    #         # Used to extract FSP IDs
    #         self.fsp_ids_object = argin_json["fsp"]
    #         self.update_config_params()
    #         self.pointing_params = argin_json["pointing"]
    #         self.target_Ra = self.pointing_params["target"]["RA"]
    #         self.target_Dec = self.pointing_params["target"]["dec"]
    #
    #         # Create target object
    #         self.target = katpoint.Target('radec , ' + str(self.target_Ra) + ", " + str(self.target_Dec))
    #
    #         cspConfiguration = argin_json.copy()
    #         # Keep configuration specific to CSP and delete pointing configuration
    #         if "pointing" in cspConfiguration:
    #             del cspConfiguration["pointing"]
    #         log_msg = "Input JSON for CSP Subarray Leaf Node Configure command is: " + argin
    #         self.logger.debug(log_msg)
    #         self.CspSubarrayProxy.command_inout_asynch(const.CMD_CONFIGURE, json.dumps(cspConfiguration),
    #                                                    self.cmd_ended_cb)
    #         self._read_activity_message = const.STR_CONFIGURE_SUCCESS
    #         self.logger.info(const.STR_CONFIGURE_SUCCESS)
    #
    #
    #     except ValueError as value_error:
    #         log_msg = const.ERR_INVALID_JSON_CONFIG + str(value_error)
    #         self.logger.error(log_msg)
    #         self._read_activity_message = const.ERR_INVALID_JSON_CONFIG + str(value_error)
    #         exception_message.append(self._read_activity_message)
    #         exception_count += 1
    #
    #     except DevFailed as dev_failed:
    #         [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
    #                             exception_message, exception_count, const.ERR_CONFIGURE_INVOKING_CMD)
    #
    #     except Exception as except_occurred:
    #         [exception_message, exception_count] = self._handle_generic_exception( except_occurred,
    #                                 exception_message, exception_count, const.ERR_CONFIGURE_INVOKING_CMD)
    #
    #     # throw exception:
    #     if exception_count > 0:
    #         self.throw_exception(exception_message, const.STR_CONFIG_SCAN_EXEC)
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.Configure



    class ConfigureCommand(ResponseCommand):
        # PROTECTED REGION ID(CspSubarrayLeafNode.Configure) ENABLED START #
        """
        A class for CspSubarrayLeafNode's Configure() command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("Configure() is not allowed in current state",
                                             "Configure() is not allowed in current state",
                                             "cspsubarrayleafnode.Configure()",
                                             tango.ErrSeverity.ERR)

            return True
        def do(self,argin):
            """
            This command configures the scan. It accepts configuration capabilities in JSON string format and
            invokes Configure command on CspSubarray with configuration capabilities in JSON string as an
            input argument.

            :param argin:DevString. The string in JSON format. The JSON contains following values:

            Example:
            {"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","fsp":[{"fspID":1,"functionMode":"CORR",
            "frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[[0,2],[744,0]],
            "fspChannelOffset":0,"outputLinkMap":[[0,0],[200,1]],"outputHost":[[0,"192.168.1.1"]],"outputPort":
            [[0,9000,1]]},{"fspID":2,"functionMode":"CORR","frequencySliceID":2,"integrationTime":1400,"corrBandwidth":0,
            "channelAveragingMap":[[0,2],[744,0]],"fspChannelOffset":744,"outputLinkMap":[[0,4],[200,5]],"outputHost":
            [[0,"192.168.1.1"]],"outputPort":[[0,9744,1]]}],"delayModelSubscriptionPoint":
            "ska_mid/tm_leaf_node/csp_subarray01/delayModel","pointing":{"target":{"system":"ICRS",
            "name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}}}

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ReturnCode, str)
            """
            device = self.target
            exception_message = []
            exception_count = 0
            try:
                argin_json = json.loads(argin)
                # Used to extract FSP IDs
                device.fsp_ids_object = argin_json["fsp"]
                device.update_config_params()
                device.pointing_params = argin_json["pointing"]
                device.target_Ra = device.pointing_params["target"]["RA"]
                device.target_Dec = device.pointing_params["target"]["dec"]

                # Create target object
                device.target = katpoint.Target('radec , ' + str(device.target_Ra) + ", " + str(device.target_Dec))

                cspConfiguration = argin_json.copy()
                # Keep configuration specific to CSP and delete pointing configuration
                if "pointing" in cspConfiguration:
                    del cspConfiguration["pointing"]
                log_msg = "Input JSON for CSP Subarray Leaf Node Configure command is: " + argin
                self.logger.debug(log_msg)
                device.CspSubarrayProxy.command_inout_asynch(const.CMD_CONFIGURE, json.dumps(cspConfiguration),
                                                           device.cmd_ended_cb)
                device._read_activity_message = const.STR_CONFIGURE_SUCCESS
                self.logger.info(const.STR_CONFIGURE_SUCCESS)
                return (ResultCode.STARTED, const.STR_CONFIGURE_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_CONFIG + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_INVALID_JSON_CONFIG + str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1
                # return (ResultCode.FAILED,const.ERR_INVALID_JSON_CONFIG)


            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                    exception_message, exception_count, const.ERR_CONFIGURE_INVOKING_CMD)
                # return (ResultCode.FAILED,const.ERR_CONFIGURE_INVOKING_CMD)

            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception( except_occurred,
                                        exception_message, exception_count, const.ERR_CONFIGURE_INVOKING_CMD)
                # return (ResultCode.FAILED, const.ERR_CONFIGURE_INVOKING_CMD)

            # throw exception:
            if exception_count > 0:
                device.throw_exception(exception_message, const.ERR_CONFIGURE_INVOKING_CMD)
                return (ResultCode.FAILED,str(exception_message))
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.Configure

    @command(
        dtype_in=('str'),
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.Configure) ENABLED START #
        """ Invokes Configure command on cspsubarrayleafnode"""
        handler = self.get_command_object("Configure")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_Configure_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
        current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
        in current device state
        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

        # PROTECTED REGION END # // CspSubarrayLeafNode.Configure

# -------------------------------------------------------------------------------------------------------

    # @command(
    #     dtype_in=('str',),
    # )
    # @DebugIt()
    # def StartScan(self, argin):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.StartScan) ENABLED START #
    #     """
    #     This command invokes Scan command on CspSubarray. It is allowed only when CspSubarray is in READY
    #     state.
    #
    #     :param argin: JSON string consists of scan id (int).
    #
    #     Example: in jive:{"id":1}
    #
    #     :return: None.
    #     """
    #     exception_message = []
    #     exception_count = 0
    #     try:
    #         #Check if CspSubarray is in READY state
    #         if self.CspSubarrayProxy.obsState == ObsState.READY:
    #             #Invoke StartScan command on CspSubarray
    #             self.CspSubarrayProxy.command_inout_asynch(const.CMD_STARTSCAN, "0", self.cmd_ended_cb)
    #             self._read_activity_message = const.STR_STARTSCAN_SUCCESS
    #             self.logger.info(const.STR_STARTSCAN_SUCCESS)
    #         else:
    #             self._read_activity_message = const.ERR_DEVICE_NOT_READY
    #             log_msg = const.STR_OBS_STATE + str(self.CspSubarrayProxy.obsState)
    #             self.logger.error(const.ERR_DEVICE_NOT_READY)
    #             self.logger.error(log_msg)
    #
    #     except DevFailed as dev_failed:
    #         [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
    #                                     exception_message, exception_count, const.ERR_STARTSCAN_RESOURCES)
    #
    #     except Exception as except_occurred:
    #         [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
    #                                     exception_message, exception_count, const.ERR_STARTSCAN_RESOURCES)
    #
    #     # throw exception:
    #     if exception_count > 0:
    #         self.throw_exception(exception_message, const.STR_START_SCAN_EXEC)
    #
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.StartScan

    class StartScanCommand(ResponseCommand):
        # PROTECTED REGION ID(CspSubarrayLeafNode.StartScan) ENABLED START #
        """
        A class for CspSubarrayLeafNode's StartScan() command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("StartScan() is not allowed in current state",
                                             "StartScan() is not allowed in current state",
                                             "cspsubarrayleafnode.StartScan()",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self, argin):
            """
            This command invokes Scan command on CspSubarray. It is allowed only when CspSubarray is in READY
            state.

            :param argin: JSON string consists of scan id (int).

            Example: in jive:{"id":1}
            :return: A tuple containing a return code and a string
                        message indicating status. The message is for
                        information purpose only.
            :rtype: (ReturnCode, str)
            """
            device=self.target
            exception_message = []
            exception_count = 0
            try:
            #Check if CspSubarray is in READY state
                if device.CspSubarrayProxy.obsState == ObsState.READY:
                    #Invoke StartScan command on CspSubarray
                    device.CspSubarrayProxy.command_inout_asynch(const.CMD_STARTSCAN, "0", device.cmd_ended_cb)
                    device._read_activity_message = const.STR_STARTSCAN_SUCCESS
                    self.logger.info(const.STR_STARTSCAN_SUCCESS)
                    return (ResultCode.STARTED,const.STR_STARTSCAN_SUCCESS)
                else:
                    device._read_activity_message = const.ERR_DEVICE_NOT_READY
                    log_msg = const.STR_OBS_STATE + str(device.CspSubarrayProxy.obsState)
                    self.logger.error(const.ERR_DEVICE_NOT_READY)
                    self.logger.error(log_msg)
                    return (ResultCode.FAILED,const.ERR_DEVICE_NOT_READY)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_STARTSCAN_RESOURCES)
                # return (ResultCode.FAILED,const.ERR_STARTSCAN_RESOURCES)

            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, const.ERR_STARTSCAN_RESOURCES)
                # return (ResultCode.FAILED, const.ERR_STARTSCAN_RESOURCES)

            # throw exception:
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_START_SCAN_EXEC)
                return (ResultCode.FAILED,const.ERR_STARTSCAN_RESOURCES)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.StartScan
    @command(
        dtype_in=('str'),
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def StartScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.StartScan) ENABLED START #
        """ Invokes StartScan command on cspsubarrayleafnode"""
        handler = self.get_command_object("StartScan")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_StartScan_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
        current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
        in current device state
        """
        handler = self.get_command_object("StartScan")
        return handler.check_allowed()

    # PROTECTED REGION END # // CspSubarrayLeafNode.StartScan

 # -------------------------------------------------------------------------------------------------------

    # @command(
    # )
    # @DebugIt()
    # def EndScan(self):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.EndScan) ENABLED START #
    #     """
    #     It invokes EndScan command on CspSubarray. This command is allowed when CspSubarray is in SCANNING
    #     state.
    #
    #     :return: None.
    #     """
    #     exception_message = []
    #     exception_count = 0
    #     try:
    #         if self.CspSubarrayProxy.obsState == ObsState.SCANNING:
    #             # Invoke EndScan command on CspSubarray
    #             self.CspSubarrayProxy.command_inout_asynch(const.CMD_ENDSCAN, self.cmd_ended_cb)
    #             self._read_activity_message = const.STR_ENDSCAN_SUCCESS
    #             self.logger.info(const.STR_ENDSCAN_SUCCESS)
    #         else:
    #             self._read_activity_message = const.ERR_DEVICE_NOT_IN_SCAN
    #             log_msg = const.STR_OBS_STATE + str(self.CspSubarrayProxy.obsState)
    #             self.logger.error(const.ERR_DEVICE_NOT_IN_SCAN)
    #             self.logger.error(log_msg)
    #
    #     except DevFailed as dev_failed:
    #         [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
    #                                     exception_message, exception_count, const.ERR_ENDSCAN_INVOKING_CMD)
    #
    #     except Exception as except_occurred:
    #         [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
    #                                     exception_message, exception_count, const.ERR_ENDSCAN_INVOKING_CMD)
    #
    #     # throw exception:
    #     if exception_count > 0:
    #         self.throw_exception(exception_message, const.STR_ENDSCAN_EXEC)
    #
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.EndScan


    class EndScanCommand(ResponseCommand):
        # PROTECTED REGION ID(CspSubarrayLeafNode.EndScan) ENABLED START #
        """
        A class for CspSubarrayLeafNode's EndScan() command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("EndScan() is not allowed in current state",
                                             "EndScan() is not allowed in current state",
                                             "cspsubarrayleafnode.EndScan()",
                                             tango.ErrSeverity.ERR)

            return True
        def do(self):
            """
            It invokes EndScan command on CspSubarray. This command is allowed when CspSubarray is in SCANNING
            state.
            :return: A tuple containing a return code and a string
                        message indicating status. The message is for
                        information purpose only.
            :rtype: (ReturnCode, str)
            """
            device=self.target
            exception_message = []
            exception_count = 0
            try:
                # Invoke EndScan command on CspSubarray
                if device.CspSubarrayProxy.obsState == ObsState.SCANNING:
                    device.CspSubarrayProxy.command_inout_asynch(const.CMD_ENDSCAN, device.cmd_ended_cb)
                    device._read_activity_message = const.STR_ENDSCAN_SUCCESS
                    self.logger.info(const.STR_ENDSCAN_SUCCESS)
                    return (ResultCode.STARTED,const.STR_ENDSCAN_SUCCESS)

                else:
                    device._read_activity_message = const.ERR_DEVICE_NOT_IN_SCAN
                    log_msg = const.STR_OBS_STATE + str(device.CspSubarrayProxy.obsState)
                    self.logger.error(const.ERR_DEVICE_NOT_IN_SCAN)
                    self.logger.error(log_msg)
                    return (ResultCode.FAILED,const.ERR_DEVICE_NOT_IN_SCAN)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_ENDSCAN_INVOKING_CMD)
                # return (ResultCode.FAILED,const.ERR_ENDSCAN_INVOKING_CMD)

            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, const.ERR_ENDSCAN_INVOKING_CMD)
                # return (ResultCode.FAILED,const.ERR_ENDSCAN_INVOKING_CMD)

            # throw exception:
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_ENDSCAN_EXEC)
                return (ResultCode.FAILED,const.ERR_ENDSCAN_INVOKING_CMD)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.EndScan

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.EndScan) ENABLED START #
        """ Invokes EndScan command on cspsubarrayleafnode"""
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_EndScan_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
        current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
        in current device state
        """
        handler = self.get_command_object("EndScan")
        return handler.check_allowed()
    # PROTECTED REGION END # // CspSubarrayLeafNode.EndScan

    # -------------------------------------------------------------------------------------------------------

    #
    # @command(
    # )
    # @DebugIt()
    # def ReleaseAllResources(self):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.ReleaseResources) ENABLED START #
    #     """
    #     It invokes RemoveAllReceptors command on CspSubarray and releases all the resources assigned to
    #     CspSubarray.
    #
    #     :return: None.
    #     """
    #     exception_message = []
    #     exception_count = 0
    #     try:
    #         #Invoke RemoveAllReceptors command on CspSubarray
    #         self.receptorIDList = []
    #         self.fsids_list = []
    #         self.update_config_params()
    #         self.CspSubarrayProxy.command_inout_asynch(const.CMD_REMOVE_ALL_RECEPTORS, self.cmd_ended_cb)
    #         self._read_activity_message = const.STR_REMOVE_ALL_RECEPTORS_SUCCESS
    #         self.logger.info(const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)
    #
    #     except DevFailed as dev_failed:
    #         [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
    #                                     exception_message, exception_count, const.ERR_RELEASE_ALL_RESOURCES)
    #     except Exception as except_occurred:
    #         [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
    #                                     exception_message, exception_count, const.ERR_RELEASE_ALL_RESOURCES)
    #
    #     # throw exception:
    #     if exception_count > 0:
    #         self.throw_exception(exception_message, const.STR_RELEASE_RES_EXEC)
    #
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.ReleaseResources


    class ReleaseAllResourcesCommand(ResponseCommand):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ReleaseResources) ENABLED START #
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("ReleaseAllResources() is not allowed in current state",
                                             "ReleaseAllResources() is not allowed in current state",
                                             "cspsubarrayleafnode.ReleaseAllResources()",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self):
            """
            It invokes RemoveAllReceptors command on CspSubarray and releases all the resources assigned to
            CspSubarray.
            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device=self.target
            exception_message = []
            exception_count = 0
            try:
                #Invoke RemoveAllReceptors command on CspSubarray
                device.receptorIDList = []
                device.fsids_list = []
                device.update_config_params()
                device.CspSubarrayProxy.command_inout_asynch(const.CMD_REMOVE_ALL_RECEPTORS, device.cmd_ended_cb)
                device._read_activity_message = const.STR_REMOVE_ALL_RECEPTORS_SUCCESS
                self.logger.info(const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)
                return (ResultCode.STARTED,const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_RELEASE_ALL_RESOURCES)
                # return (ResultCode.FAILED,const.ERR_RELEASE_ALL_RESOURCES)

            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, const.ERR_RELEASE_ALL_RESOURCES)
                # return (ResultCode.FAILED, const.ERR_RELEASE_ALL_RESOURCES)

            # throw exception:
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_RELEASE_RES_EXEC)
                return (ResultCode.FAILED,const.ERR_RELEASE_ALL_RESOURCES)

        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ReleaseResources
    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ReleaseAllResources) ENABLED START #
        """ Invokes ReleaseAllResources command on cspsubarrayleafnode"""
        handler = self.get_command_object("ReleaseAllResources")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_ReleaseAllResources_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
        current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
        in current device state
        """
        handler = self.get_command_object("ReleaseAllResources")
        return handler.check_allowed()
    # PROTECTED REGION END # // CspSubarrayLeafNode.ReleaseAllResources

    # -------------------------------------------------------------------------------------------------------
        # PROTECTED REGION END # // CspSubarrayLeafNode.AssignResources
    #
    # @command(
    #     dtype_in=('str',),
    # )
    # @DebugIt()
    # def AssignResources(self, argin):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.AssignResources) ENABLED START #
    #     """
    #     It accepts receptor id list in JSON string format and invokes AddReceptors command on CspSubarray
    #     with receptorIDList (list of integers) as an input argument.
    #
    #     :param argin: The string in JSON format. The JSON contains following values:
    #
    #         dish:
    #             Mandatory JSON object consisting of
    #
    #             receptorIDList:
    #                 DevVarString
    #                 The individual string should contain dish numbers in string format
    #                 with preceding zeroes upto 3 digits. E.g. 0001, 0002.
    #     Example:
    #             {
    #             "subarrayID": 1,
    #             "dish": {
    #             "receptorIDList": ["0001", "0002"]
    #             }
    #             }
    #
    #      Note: Enter input without spaces as:{"subarrayID":1,"dish":{"receptorIDList":["0001","0002"]}}
    #     :return: None.
    #     """
    #     exception_message = []
    #     exception_count = 0
    #     try:
    #         #Parse receptorIDList from JSON string.
    #         jsonArgument = json.loads(argin[0])
    #         self.receptorIDList_str = jsonArgument[const.STR_DISH][const.STR_RECEPTORID_LIST]
    #         #convert receptorIDList from list of string to list of int
    #         for i in range(0, len(self.receptorIDList_str)):
    #             self.receptorIDList.append(int(self.receptorIDList_str[i]))
    #         self.update_config_params()
    #         # Invoke AddReceptors command on CspSubarray
    #         self.CspSubarrayProxy.command_inout_asynch(const.CMD_ADD_RECEPTORS, self.receptorIDList,
    #                                                        self.cmd_ended_cb)
    #         self._read_activity_message = const.STR_ADD_RECEPTORS_SUCCESS
    #         self.logger.info(const.STR_ADD_RECEPTORS_SUCCESS)
    #
    #     except ValueError as value_error:
    #         log_msg = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
    #         self.logger.error(log_msg)
    #         self._read_activity_message = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
    #         exception_message.append(self._read_activity_message)
    #         exception_count += 1
    #     except KeyError as key_error:
    #         log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
    #         self.logger.error(log_msg)
    #         self._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
    #         exception_message.append(self._read_activity_message)
    #         exception_count += 1
    #
    #     except DevFailed as dev_failed:
    #         [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
    #                                      exception_message, exception_count, const.ERR_ASSGN_RESOURCES)
    #
    #
    #     except Exception as except_occurred:
    #         [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
    #                                      exception_message, exception_count, const.ERR_ASSGN_RESOURCES)
    #
    #     # throw exception:
    #     if exception_count:
    #         print ("Exception in AssignResource:", exception_message)
    #         self.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)
    #
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.AssignResources

    class AssignResourcesCommand(ResponseCommand):
        # PROTECTED REGION ID(CspSubarrayLeafNode.AssignResources) ENABLED START #
        """
        A class for CspSubarrayLeafNode's AssignResources command.
        """

        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("AssignResources() is not allowed in current state",
                                             "AssignResources() is not allowed in current state",
                                             "cspsubarrayleafnode.AssignResources()",
                                             tango.ErrSeverity.ERR)

            return True

        def do(self,argin):
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
            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device=self.target
            exception_message = []
            exception_count = 0
            try:
                #Parse receptorIDList from JSON string.
                jsonArgument = json.loads(argin[0])
                device.receptorIDList_str = jsonArgument[const.STR_DISH][const.STR_RECEPTORID_LIST]
                #convert receptorIDList from list of string to list of int
                for i in range(0, len(device.receptorIDList_str)):
                    device.receptorIDList.append(int(device.receptorIDList_str[i]))
                device.update_config_params()
                # Invoke AddReceptors command on CspSubarray
                device.CspSubarrayProxy.command_inout_asynch(const.CMD_ADD_RECEPTORS, device.receptorIDList,
                                                               device.cmd_ended_cb)
                device._read_activity_message = const.STR_ADD_RECEPTORS_SUCCESS
                self.logger.info(const.STR_ADD_RECEPTORS_SUCCESS)
                return (ResultCode.STARTED,const.STR_ADD_RECEPTORS_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1
                # return (ResultCode.FAILED,const.ERR_INVALID_JSON_ASSIGN_RES)

            except KeyError as key_error:
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                self.logger.error(log_msg)
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                exception_message.append(device._read_activity_message)
                exception_count += 1
                # return (ResultCode.FAILED,const.ERR_JSON_KEY_NOT_FOUND)

            except DevFailed as dev_failed:
                [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                             exception_message, exception_count, const.ERR_ASSGN_RESOURCES)
                # return (ResultCode.FAILED,const.ERR_ASSGN_RESOURCES)


            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                             exception_message, exception_count, const.ERR_ASSGN_RESOURCES)
                # return (ResultCode.FAILED,const.ERR_ASSGN_RESOURCES)

            # throw exception:
            if exception_count>0:
                print ("Exception in AssignResource:", exception_message)
                self.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)
                return (ResultCode.FAILED,str(exception_message))

    # PROTECTED REGION END #    //  CspSubarrayLeafNode.AssignResources

    @command(
        dtype_in=('str',),
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.AssignResources) ENABLED START #
        """ Invokes AssignResources command on cspsubarrayleafnode"""
        handler = self.get_command_object("AssignResources")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_AssignResources_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
        current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
        in current device state
        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

        # PROTECTED REGION END # // CspSubarrayLeafNode.AssignResources

 # -------------------------------------------------------------------------------------------------------

    # @command(
    # )
    # @DebugIt()
    # def GoToIdle(self):
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.GoToIdle) ENABLED START #
    #     """
    #     This command invokes GoToIdle command on CSP Subarray in order to end current scheduling block.
    #
    #     :return: None.
    #
    #     """
    #     exception_message = []
    #     exception_count = 0
    #     try:
    #         if self.CspSubarrayProxy.obsState == ObsState.READY:
    #             self.CspSubarrayProxy.command_inout_asynch(const.CMD_GOTOIDLE, self.cmd_ended_cb)
    #             self._read_activity_message = const.STR_GOTOIDLE_SUCCESS
    #             self.logger.info(const.STR_GOTOIDLE_SUCCESS)
    #         else:
    #             self._read_activity_message = const.ERR_DEVICE_NOT_READY
    #             log_msg = const.STR_OBS_STATE + str(self.CspSubarrayProxy.obsState)
    #             self.logger.error(const.ERR_DEVICE_NOT_READY)
    #             self.logger.error(log_msg)
    #     except DevFailed as dev_failed:
    #         [ exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
    #                                     exception_message, exception_count, const.ERR_GOTOIDLE_INVOKING_CMD)
    #
    #     except Exception as except_occurred:
    #         [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
    #                                     exception_message, exception_count, const.ERR_GOTOIDLE_INVOKING_CMD)
    #
    #     # throw exception:
    #     if exception_count > 0:
    #         self.throw_exception(exception_message, const.STR_GOTOIDLE_EXEC)
    #
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.GoToIdle

    class GoToIdleCommand(ResponseCommand):
        # PROTECTED REGION ID(CspSubarrayLeafNode.GoToIdle) ENABLED START #
        """
        A class for CspSubarrayLeafNode's GoToIdle command.
        """
        def check_allowed(self):
            """
            Whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in
                current device state
            :rtype: boolean
            :raises: DevFailed if this command is not allowed to be run
                in current device state
            """
            if self.state_model.dev_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("GoToIdle() is not allowed in current state",
                                             "GoToIdle() is not allowed in current state",
                                             "cspsubarrayleafnode.GoToIdle()",
                                             tango.ErrSeverity.ERR)

            return True
        def do(self):
            """
            This command invokes GoToIdle command on CSP Subarray in order to end current scheduling block.
            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device=self.target
            exception_message = []
            exception_count = 0
            try:
                if device.CspSubarrayProxy.obsState == ObsState.READY:
                    device.CspSubarrayProxy.command_inout_asynch(const.CMD_GOTOIDLE, device.cmd_ended_cb)
                    device._read_activity_message = const.STR_GOTOIDLE_SUCCESS
                    self.logger.info(const.STR_GOTOIDLE_SUCCESS)
                    return (ResultCode.STARTED,const.STR_GOTOIDLE_SUCCESS)
                else:
                    device._read_activity_message = const.ERR_DEVICE_NOT_READY
                    log_msg = const.STR_OBS_STATE + str(device.CspSubarrayProxy.obsState)
                    self.logger.error(const.ERR_DEVICE_NOT_READY)
                    self.logger.error(log_msg)
                    return (ResultCode.FAILED,const.ERR_DEVICE_NOT_READY)

            except DevFailed as dev_failed:
                [ exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_GOTOIDLE_INVOKING_CMD)
                # return (ResultCode.FAILED,const.ERR_GOTOIDLE_INVOKING_CMD)

            except Exception as except_occurred:
                [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, const.ERR_GOTOIDLE_INVOKING_CMD)
                # return (ResultCode.FAILED,const.ERR_GOTOIDLE_INVOKING_CMD)

            # throw exception:
            if exception_count > 0:
                self.throw_exception(exception_message, const.STR_GOTOIDLE_EXEC)
                return (ResultCode.FAILED,const.ERR_GOTOIDLE_INVOKING_CMD)
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.GoToIdle

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def GoToIdle (self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.GoToIdle) ENABLED START #
        """ Invokes GoToIdle command on cspsubarrayleafnode"""
        handler = self.get_command_object("GoToIdle")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_GoToIdle_allowed(self):
        """
        Whether this command is allowed to be run in current device
        state
        :return: True if this command is allowed to be run in
        current device state
        :rtype: boolean
        :raises: DevFailed if this command is not allowed to be run
        in current device state
        """
        handler = self.get_command_object("GoToIdle")
        return handler.check_allowed()
     # PROTECTED REGION END #    //  CspSubarrayLeafNode.GoToIdle
# -------------------------------------------------------------------------------------------------------

    # class OnCommand(SKASubarray.OnCommand):
    #     """
    #     A class for the cspsubarrayleafnode's On() command.
    #     """
    #
    #     def do(self):
    #         """
    #         Stateless hook for On() command functionality.
    #
    #         :return: A tuple containing a return code and a string
    #             message indicating status. The message is for
    #             information purpose only.
    #         :rtype: (ResultCode, str)
    #         """
    #         device = self.target
    #         print("On command device object:", device)
    #         message = "On command completed OK"
    #         self.logger.info(message)
    #         return (ResultCode.OK, message)


# pylint: enable=protected-access,unused-argument,unused-variable

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
