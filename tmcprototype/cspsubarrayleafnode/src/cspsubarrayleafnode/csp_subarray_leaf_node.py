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
from tango import DebugIt, AttrWriteType, DeviceProxy, DevFailed
from tango.server import run, attribute, command, device_property
import katpoint

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState
from . import const, release, assign_resources_command, release_all_resources_command, configure_command,\
    scan_command, end_scan_command, end_command, abort_command, restart_command, obsreset_command
from .exceptions import InvalidObsStateError
from .device_data import DeviceData
# PROTECTED REGION END #    //  CspSubarrayLeafNode.additional_import

__all__ = ["CspSubarrayLeafNode", "main", "assign_resources_command", "release_all_resources_command",
           "configure_command", "scan_command", "end_scan_command", "end_command", "abort_command", 
           "restart_command", "obsreset_command"]


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
            device_data = DeviceData.get_instance()
            device_data.csp_subarray_fqdn = device.CspSubarrayFQDN
            
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

            # TODO: Should we create object of delay Model class here?
            
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
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_EMPTY_OR_IDLE,
                                         "CSP subarray leaf node raised exception",
                                         "CSP.AddReceptors",
                                         tango.ErrSeverity.ERR)
        handler(argin)

    
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
        if self._csp_subarray_proxy.obsState in [ObsState.EMPTY, ObsState.IDLE]:
            self.logger.info("CSP Subarray is in required obsState, resources will be assigned")
        else:
            self.logger.error("CSP Subarray is not in EMPTY/IDLE obsState")
            self._read_activity_message = "Error in device obsState"
            raise InvalidObsStateError("CSP Subarray is not in EMPTY/IDLE obsState")

    
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
        self.register_command_object("AssignResources", assign_resources_command.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseAllResources", release_all_resources_command.ReleaseAllResourcesCommand(*args))
        self.register_command_object("Configure", configure_command.ConfigureCommand(*args))
        self.register_command_object("StartScan", scan_command.StartScanCommand(*args))
        self.register_command_object("EndScan", end_scan_command.EndScanCommand(*args))
        self.register_command_object("GoToIdle", end_command.GoToIdleCommand(*args))
        self.register_command_object("Abort", abort_command.AbortCommand(*args))
        self.register_command_object("Restart", restart_command.RestartCommand(*args))
        self.register_command_object("ObsReset", obsreset_command.ObsResetCommand(*args))


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
