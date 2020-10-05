# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Subarray Node Low
Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a Subarray.
"""

# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, device_property

# Additional imports
from ska.base.commands import ResultCode
from ska.base.control_model import HealthState, ObsMode, ObsState
from ska.base import SKASubarray
from . import const, release, on_command, assign_resources_command, configure_command, scan_command, end_scan_command, end_command, release_all_resources_command, off_command

__all__ = ["SubarrayNode", "main", "assign_resources_command", "release_all_resources_command",
           "configure_command", "scan_command", "end_scan_command", "end_command", "on_command",
           "off_command"]


class SubarrayHealthState:

    @staticmethod
    def generate_health_state_log_msg(health_state, device_name, event):
        if isinstance(health_state, HealthState):
            return (
                const.STR_HEALTH_STATE + str(device_name) + const.STR_ARROW + str(health_state.name.upper()))
        else:
            return const.STR_HEALTH_STATE_UNKNOWN_VAL + str(event)

    @staticmethod
    def calculate_health_state(health_states):
        """
        Calculates aggregated health state of SubarrayLow.
        """
        unique_states = set(health_states)
        if unique_states == set([HealthState.OK]):
            return HealthState.OK
        elif HealthState.FAILED in unique_states:
            return HealthState.FAILED
        elif HealthState.DEGRADED in unique_states:
            return HealthState.DEGRADED
        else:
            return HealthState.UNKNOWN

class SubarrayNode(SKASubarray):
    """
    Provides the monitoring and control interface required by users as well as
    other TM Components (such as OET, Central Node) for a Subarray.
    """
    def command_class_object(self):
        """
        Sets up the command objects
        :return: None
        """
        args = (self, self.state_model, self.logger)
        self.init_obj = self.InitCommand(*args)
        self.on_obj = on_command.OnCommand(*args)
        self.off_obj = off_command.OffCommand(*args)
        self.end_obj = end_command.EndCommand(*args)
        self.scan_obj = scan_command.ScanCommand(*args)
        self.endscan_obj = end_scan_command.EndScanCommand(*args)
        self.configure_obj = configure_command.ConfigureCommand(*args)
        self.release_obj = release_all_resources_command.ReleaseAllResourcesCommand(*args)
        self.assign_obj = assign_resources_command.AssignResourcesCommand(*args)

    def health_state_cb(self, event):
        """
        Receives the subscribed health states, aggregates them
        to calculate the overall subarray health state.

        :param evt: A event on MCCS Subarray healthState.

        :type: Event object
            It has the following members:
                    
                - date (event timestamp)

                - reception_date (event reception timestamp)

                - type (event type)

                - dev_name (device name)

                - name (attribute name)

                - value (event value)

        :return: None
        """

        device_name = event.device.dev_name()
        if not event.err:
            event_health_state = event.attr_value.value
            self.subarray_ln_health_state_map[device_name] = event_health_state

            log_message = SubarrayHealthState.generate_health_state_log_msg(
                event_health_state, device_name, event)
            self._read_activity_message = log_message
            self._health_state = SubarrayHealthState.calculate_health_state(
                self.subarray_ln_health_state_map.values())
        else:
            log_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(device_name) + str(event)
            self._read_activity_message = log_message

    def observation_state_cb(self, evt):
        """
        Receives the subscribed MCCS Subarray obsState.

        :param evt: A event on MCCS Subarray ObsState.

        :type: Event object
            It has the following members:
                    
                - date (event timestamp)

                - reception_date (event reception timestamp)

                - type (event type)

                - dev_name (device name)

                - name (attribute name)

                - value (event value)

        :return: None

        :raises: KeyError if error occurs while setting SubarrayNode's ObsState.
        """
        try:
            if not evt.err:
                self._observetion_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TMMCCS_MID_SALN in evt.attr_name:
                    self._mccs_sa_obs_state = self._observetion_state
                    self._read_activity_message = const.STR_MCCS_SUBARRAY_OBS_STATE + str(
                        self._mccs_sa_obs_state)
                else:
                    self.logger.debug(const.EVT_UNKNOWN)
                    self._read_activity_message = const.EVT_UNKNOWN
                self.calculate_observation_state()

            else:
                log_msg = const.ERR_SUBSR_MCCSSA_OBS_STATE + str(evt)
                self.logger.debug(log_msg)
                self._read_activity_message = log_msg
        except KeyError as key_error:
            log_msg = const.ERR_MCCS_SUBARRAY_OBS_STATE + str(key_error)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_MCCS_SUBARRAY_OBS_STATE + str(key_error)

    def calculate_observation_state(self):
        """
        Calculates aggregated observation state of Subarray.
        """
        log_msg = "self._mccs_sa_obs_state is: " + str(self._mccs_sa_obs_state)
        self.logger.info(log_msg)
        if self._mccs_sa_obs_state == ObsState.EMPTY:
            if self.is_release_resources:
                self.logger.info("Calling ReleaseAllResource command succeeded() method")
                self.release_obj.succeeded()

        elif self._mccs_sa_obs_state == ObsState.READY:
            if self.is_scan_completed:
                self.logger.info("Calling EndScan command succeeded() method")
                self.endscan_obj.succeeded()
            else:
                # Configure command success
                self.logger.info("Calling Configure command succeeded() method")
                self.configure_obj.succeeded()
        elif self._mccs_sa_obs_state == ObsState.IDLE:
            if self.is_end_command:
                # End command success
                self.logger.info("Calling End command succeeded() method")
                self.end_obj.succeeded()
            else:
                # Assign Resource command success
                self.logger.info("Calling AssignResource command succeeded() method")
                self.assign_obj.succeeded()


    def get_deviceproxy(self, device_fqdn):
        """
        Returns device proxy for given FQDN.
        """
        retry = 0
        device_proxy = None
        while retry < 3:
            try:
                device_proxy = DeviceProxy(device_fqdn)
                break
            except DevFailed as df:
                self.logger.exception(df)
                if retry >= 2:
                    tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                    "Failed to create DeviceProxy of " + str(device_fqdn),
                                                    "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                retry += 1
                continue
        return device_proxy

    def __len__(self):
        """
        Returns the number of resources currently assigned. Note that
        this also functions as a boolean method for whether there are
        any assigned resources: ``if len()``.

        :return: number of resources assigned
        :rtype: int
        """

        return len(self._resource_list)

    # -----------------
    # Device Properties
    # -----------------

    MccsSubarrayLNFQDN = device_property(
        dtype='str', doc="This property contains the FQDN of the MCCS Subarray Leaf Node associated with the "
                         "Subarray Node."
    )

    MccsSubarrayFQDN = device_property(
        dtype='str', doc="This property contains the FQDN of the MCCS Subarray associated with the "
                         "Subarray Node."
    )

    MccsSubarrayFQDN = device_property(
        dtype='str',
    )


    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype='str',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKASubarray.InitCommand):
        """
        A class for the TMC SubarrayNode's init_device() method.
        """
        def do(self):
            """
            Initializes the attributes and properties of the Subarray Node.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if the error while subscribing the tango attribute
            """
            super().do()
            device = self.target
            device.set_status(const.STR_SA_INIT)
            device._obs_mode = ObsMode.IDLE
            device._scan_id = ""
            device._resource_list = []
            device.is_end_command = False
            device.is_release_resources = False
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            device._health_event_id = []
            device._mccs_sa_obs_state = ObsState.EMPTY
            device.subarray_ln_health_state_map = {}
            device._subarray_health_state = HealthState.OK  #Aggregated Subarray Health State

            # Create proxy for MCCS Subarray Leaf Node
            device._mccs_subarray_ln_proxy = None
            device._mccs_subarray_proxy = None
            device._mccs_subarray_ln_proxy = device.get_deviceproxy(device.MccsSubarrayLNFQDN)
            device._mccs_subarray_proxy = device.get_deviceproxy(device.MccsSubarrayFQDN)
            device.command_class_object()

            try:
                device.subarray_ln_health_state_map[device._mccs_subarray_ln_proxy.dev_name()] = (
                    HealthState.UNKNOWN)
                # Subscribe mccssubarrayHealthState (forwarded attribute) of MccsSubarray
                device._mccs_subarray_ln_proxy.subscribe_event(const.EVT_MCCSSA_HEALTH, EventType.CHANGE_EVENT,
                                                              device.health_state_cb, stateless=True)

                # Subscribe mccsSubarrayObsState (forwarded attribute) of MccsSubarray
                device._mccs_subarray_ln_proxy.subscribe_event(const.EVT_MCCSSA_OBS_STATE, EventType.CHANGE_EVENT,
                                                              device.observation_state_cb, stateless=True)
                device.set_status(const.STR_SUB_ATTR_MCCS_SALN_SUCCESS)
                self.logger.info(const.STR_SUB_ATTR_MCCS_SALN_SUCCESS)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBS_MCCS_SA_LEAF_ATTR + str(dev_failed)
                device._read_activity_message = log_msg
                device.set_status(const.ERR_SUBS_MCCS_SA_LEAF_ATTR)
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_SUBS_MCCS_SA_LEAF_ATTR,
                                             log_msg,
                                             "SubarrayNode.InitCommand",
                                             tango.ErrSeverity.ERR)



            device._read_activity_message = const.STR_SA_INIT_SUCCESS
            self.logger.info(device._read_activity_message)
            return (ResultCode.OK, device._read_activity_message)

    def always_executed_hook(self):
        """ Internal construct of TANGO. """
        # PROTECTED REGION ID(SubarrayNode.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SubarrayNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SubarrayNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        """ Internal construct of TANGO. Returns the Scan ID.

        EXAMPLE: 123
        Where 123 is a Scan ID from configuration json string.
        """
        # PROTECTED REGION ID(SubarrayNode.scanID_read) ENABLED START #
        return self._scan_id
        # PROTECTED REGION END #    //  SubarrayNode.scanID_read

    def read_activityMessage(self):
        """ Internal construct of TANGO. Returns activityMessage.
        Example: "Subarray node is initialized successfully"
        //result occured after initialization of device.
        """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_read) ENABLED START #
        return self._read_activity_message
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_read

    def write_activityMessage(self, value):
        """ Internal construct of TANGO. Sets the activityMessage. """
        # PROTECTED REGION ID(SubarrayNode.activityMessage_write) ENABLED START #
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SubarrayNode.activityMessage_write

    # --------
    # Commands
    # --------

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        args = (self, self.state_model, self.logger)
        self.register_command_object("AssignResources", assign_resources_command.AssignResourcesCommand(*args))
        self.register_command_object("ReleaseAllResources", release_all_resources_command.ReleaseAllResourcesCommand(*args))
        self.register_command_object("On", on_command.OnCommand(*args))
        self.register_command_object("Off", off_command.OffCommand(*args))
        self.register_command_object("Configure", configure_command.ConfigureCommand(*args))
        self.register_command_object("Scan", scan_command.ScanCommand(*args))
        self.register_command_object("End", end_command.EndCommand(*args))
        self.register_command_object("EndScan", end_scan_command.EndScanCommand(*args))
        self.register_command_object("ReleaseAllResources", release_all_resources_command.ReleaseAllResourcesCommand(*args))


# ----------
# Run server
# ----------

def main(args=None, **kwargs):
    # PROTECTED REGION ID(SubarrayNode.main) ENABLED START #
    """
    Runs the SubarrayNode.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: SubarrayNode TANGO object.
    """
    return run((SubarrayNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SubarrayNode.main

if __name__ == '__main__':
    main()