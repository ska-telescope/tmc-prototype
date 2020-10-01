# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution.

"""
# PROTECTED REGION ID(SdpSubarrayLeafNode.additionnal_import) ENABLED START #
# PyTango imports
import tango
from tango import DeviceProxy, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState
from ska.base.commands import ResultCode, ResponseCommand, BaseCommand
# Additional imports
from . import const, release
from .exceptions import InvalidObsStateError

# PROTECTED REGION END #    //  SdpSubarrayLeafNode.additionnal_import
__all__ = ["SdpSubarrayLeafNode", "main"]


# pylint: disable=unused-argument,unused-variable, implicit-str-concat
class SdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
    """
    # -----------------
    # Device Properties
    # -----------------
    SdpSubarrayFQDN = device_property(
        dtype='str', doc='FQDN of the SDP Subarray Tango Device Server.'
    )

    # ----------
    # Attributes
    # ----------
    receiveAddresses = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc='This attribute is used for testing purposes. In the unit test cases, '
            'it is used to provide FQDN of receiveAddresses attribute from SDP.',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc='String providing information about the current activity in SDP Subarray Leaf Node',
    )

    activeProcessingBlocks = attribute(
        dtype='str',
        doc='This is a attribute from SDP Subarray which depicts the active Processing Blocks in '
            'the SDP Subarray.',
    )

    sdpSubarrayHealthState = attribute(name="sdpSubarrayHealthState", label="sdpSubarrayHealthState",
                                       forwarded=True)

    sdpSubarrayObsState = attribute(name="sdpSubarrayObsState", label="sdpSubarrayObsState", forwarded=True)

    # ---------------
    # General methods
    # ---------------
    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TMC SdpSubarrayLeafNode's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the SdpSubarrayLeafNode.

            :return: A tuple containing a return code and a string message indicating status.
                     The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            super().do()
            device = self.target
            # Initialise device state
            device.set_status(const.STR_SDPSALN_INIT_SUCCESS)

            # Initialise attributes
            device._receive_addresses = ""
            device._sdp_subarray_health_state = HealthState.OK
            device._read_activity_message = ""
            device._active_processing_block = ""
            device._build_state = '{},{},{}'.format(release.name, release.version, release.description)
            device._version_id = release.version
            # Initialise Device status
            device.set_status(const.STR_SDPSALN_INIT_SUCCESS)
            self.logger.info(const.STR_SDPSALN_INIT_SUCCESS)
            device._read_activity_message = const.STR_SDPSALN_INIT_SUCCESS

            # Create Device proxy for Sdp Subarray using SdpSubarrayFQDN property
            device._sdp_subarray_proxy = DeviceProxy(device.SdpSubarrayFQDN)
            return (ResultCode.OK, const.STR_SDPSALN_INIT_SUCCESS)

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
        self.register_command_object("Scan", self.ScanCommand(*args))
        self.register_command_object("EndScan", self.EndScanCommand(*args))
        self.register_command_object("EndSB", self.EndSBCommand(*args))
        self.register_command_object("Abort", self.AbortCommand(*args))
        self.register_command_object("Restart", self.RestartCommand(*args))
        self.register_command_object("ObsReset", self.ObsResetCommand(*args))


    def always_executed_hook(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_receiveAddresses(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.receiveAddresses_read) ENABLED START #
        """ Internal construct of TANGO. Returns the Receive Addresses.
        receiveAddresses is a forwarded attribute from SDP Master which depicts State of the SDP."""
        return self._receive_addresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.receiveAddresses_read

    def write_receiveAddresses(self, value):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.receiveAddresses_read) ENABLED START #
        """ Internal construct of TANGO. Sets the Receive Addresses.
        receiveAddresses is a forwarded attribute from SDP Master which depicts State of the SDP."""
        self._receive_addresses = value
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.receiveAddresses_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_read) ENABLED START #
        """ Internal construct of TANGO. Returns Activity Messages.
        activityMessage is a String providing information about the current activity in SDP Subarray Leaf Node"""
        return self._read_activity_message
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_write) ENABLED START #
        """Internal construct of TANGO. Sets the Activity Message.
        activityMessage is a String providing information about the current activity in SDP Subarray Leaf Node."""
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_write

    def read_activeProcessingBlocks(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activeProcessingBlocks_read) ENABLED START #
        """Internal construct of TANGO. Returns Active Processing Blocks.activeProcessingBlocks is a forwarded attribute
         from SDP Subarray which depicts the active Processing Blocks in the SDP Subarray"""
        return self._active_processing_block
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activeProcessingBlocks_read

    def validate_obs_state(self):
        sdp_subarray_obs_state = self._sdp_subarray_proxy.obsState
        if sdp_subarray_obs_state == ObsState.EMPTY:
            self.logger.info("SDP subarray is in required obstate,Hence resources to SDP can be assign.")
        else:
            self.logger.error("Subarray is not in EMPTY obstate")
            self._read_activity_message = "Error in device obstate."
            raise InvalidObsStateError("SDP subarray is not in EMPTY obstate.")

    # --------
    # Commands
    # --------

    class ReleaseAllResourcesCommand(ResponseCommand):
        """
        A class for SdpSubarayLeafNode's ReleaseAllResources() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: Exception if command execution throws any type of exception

            """

            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("ReleaseAllResources() is not allowed in current state",
                                             "Failed to invoke ReleaseAllResources command on "
                                             "SdpSubarrayLeafNode.",
                                             "SdpSubarrayLeafNode.ReleaseAllResources()",
                                             tango.ErrSeverity.ERR)
            return True

        def releaseallresources_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the releaseallresources command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
                          callback model for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            Releases all the resources of given SDPSubarrayLeafNode. It accepts the subarray id,
            releaseALL flag and receptorIDList in JSON string format.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
                     The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if the command execution is not successful.
            """
            device = self.target
            try:
                # Call SDP Subarray Command asynchronously
                device.response = device._sdp_subarray_proxy.command_inout_asynch(const.CMD_RELEASE_RESOURCES,
                                                                                 self.releaseallresources_cmd_ended_cb)
                # Update the status of command execution status in activity message
                device._read_activity_message = const.STR_REL_RESOURCES
                self.logger.info(const.STR_REL_RESOURCES)
                return(ResultCode.OK, const.STR_REL_RESOURCES)

            except DevFailed as dev_failed:
                log_msg = const.ERR_RELEASE_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.ReleaseAllResourcesCommand()",
                                             tango.ErrSeverity.ERR)

    def is_ReleaseAllResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """

        handler = self.get_command_object("ReleaseAllResources")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        """
        Invokes ReleaseAllResources command on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("ReleaseAllResources")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class AssignResourcesCommand(ResponseCommand):
        """
        A class for SdpSubarayLeafNode's AssignResources() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: Exception if command execution throws any type of exception.

            """

            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("AssignResources() is not allowed in current state",
                                        "Failed to invoke AssignResources command on SdpSubarrayLeafNode.",
                                        "sdpsubarrayleafnode.AssignResources()",
                                        tango.ErrSeverity.ERR)

            return True

        def AssignResources_ended(self, event):
            """
            This is the callback method of AssignResources command of the SDP Subarray.
            It checks whether the AssignResources command on SDP subarray is successful.

            :param argin:

                event: response from SDP Subarray for the invoked assign resource command.

            :return: None
            """
            device = self.target
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
                tango.Except.throw_exception(
                    "SDP Subarray returned error while assigning resources",
                    str(event.errors),
                    event.cmd_name,
                    tango.ErrSeverity.ERR
                )
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.debug(log)

        def do(self, argin):
            """
            Assigns resources to given SDP subarray.
            This command is provided as a noop placeholder from SDP subarray.
            Eventually this will likely take a JSON string specifying the resource request.

            :param argin: The string in JSON format. The JSON contains following values:

            SBI ID and maximum length of the SBI:
                Mandatory JSON object consisting of

                SBI ID :
                    String

                max_length:
                    Float

            Scan types:
                Consist of Scan type id name

                scan_type:
                    DevVarStringArray

            Processing blocks:
                Mandatory JSON object consisting of

                    processing_blocks:
                        DevVarStringArray

            Example:
                {"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A",
                "coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","channels":[{"count"
                :744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],
                [744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,
                "link_map":[[2000,4],[2200,5]]}]},{"id":"calibration_B","coordinate_system":"ICRS","ra":
                "12:29:06.699","dec":"02:03:08.598","channels":[{"count":744,"start":0,"stride":2,
                "freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,
                "start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]}]
                ,"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":
                "vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":
                {"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},{"id":
                "pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"},"parameters"
                :{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":
                "pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},"parameters"
                :{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":["calibration"]}]}]}

            Note: Enter input without spaces

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: ValueError if input argument json string contains invalid value.
                     DevFailed if the command execution is not successful.
            """
            device = self.target
            try:
                device.validate_obs_state()

                # Call SDP Subarray Command asynchronously
                device.response = device._sdp_subarray_proxy.command_inout_asynch(const.CMD_ASSIGN_RESOURCES, argin,
                                                                                  self.AssignResources_ended)
                # Update the status of command execution status in activity message
                device._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
                self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)
                return ResultCode.OK, const.STR_ASSIGN_RESOURCES_SUCCESS
            except InvalidObsStateError as error:
                self.logger.exception(error)
                tango.Except.throw_exception("obstate is not in EMPTY state", str(error),
                                             "SDP.AssignResources", tango.ErrSeverity.ERR)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON + str(value_error)
                self.logger.exception(log_msg)
                device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                             const.ERR_INVALID_JSON, tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.AssignResourcesCommand()",
                                             tango.ErrSeverity.ERR)

    @command(
        dtype_in=('str'),
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        Assigns resources to given SDP subarray.
        """
        handler = self.get_command_object("AssignResources")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_AssignResources_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        """
        handler = self.get_command_object("AssignResources")
        return handler.check_allowed()

    class ConfigureCommand(ResponseCommand):
        """
        A class for SdpSubarrayLeafNode's Configure() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: Exception if command execution throws any type of exception

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Configure() is not allowed in current state",
                                             "Failed to invoke Configure command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.Configure()",
                                             tango.ErrSeverity.ERR)
            return True

        def configure_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the configure command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
                          callback model for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self, argin):
            """
            Configures the SDP Subarray device by providing the SDP PB
            configuration needed to execute the receive workflow

            :param argin: The string in JSON format. The JSON contains following values:

            Example:

            { "scan_type": "science_A" }

            :return: A tuple containing a return code and a string message indicating status.
                     The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: ValueError if input argument json string contains invalid value.
                     KeyError if input argument json string contains invalid key.
                     DevFailed if the command execution is not successful
            """
            device = self.target
            try:
                log_msg = "Input JSON for SDP Subarray Leaf Node Configure command is: " + argin
                self.logger.debug(log_msg)
                device._sdp_subarray_proxy.command_inout_asynch(const.CMD_CONFIGURE, argin,
                                                              self.configure_cmd_ended_cb)
                device._read_activity_message = const.STR_CONFIGURE_SUCCESS
                self.logger.info(const.STR_CONFIGURE_SUCCESS)
                return(ResultCode.OK, const.STR_CONFIGURE_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_CONFIGURE + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.ConfigureCommand()",
                                             tango.ErrSeverity.ERR)


    def is_Configure_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        """
        handler = self.get_command_object("Configure")
        return handler.check_allowed()

    @command(
        dtype_in=('str'),
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def Configure(self, argin):
        """
        Invokes Configure on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("Configure")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class ScanCommand(ResponseCommand):
        """
        A class for SdpSubarrayLeafNode's Scan() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: Exception if command execution throws any type of exception.

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Scan() is not allowed in current state",
                                             "Failed to invoke Scan command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.Scan()",
                                             tango.ErrSeverity.ERR)
            return True

        def scan_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the scan command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
             for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self, argin):
            """
            Invoke Scan command to SDP subarray.

            :param argin: The string in JSON format. The JSON contains following values:

            Example:
            {“id”:1}

            Note: Enter input as without spaces:{“id”:1}

            :return: A tuple containing a return code and a string message indicating status.
                     The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if the command execution is not successful.
            """
            device = self.target
            try:
                sdp_subarray_obs_state = device._sdp_subarray_proxy.obsState
                # Check if SDP Subarray obsState is READY
                if sdp_subarray_obs_state == ObsState.READY:
                    log_msg = "Input JSON for SDP Subarray Leaf Node Scan command is: " + argin
                    self.logger.debug(log_msg)
                    device._sdp_subarray_proxy.command_inout_asynch(const.CMD_SCAN, argin,
                                                                    self.scan_cmd_ended_cb)
                    device._read_activity_message = const.STR_SCAN_SUCCESS
                    self.logger.info(const.STR_SCAN_SUCCESS)
                    return(ResultCode.OK, const.STR_SCAN_SUCCESS)
                else:
                    device._read_activity_message = const.ERR_DEVICE_NOT_READY
                    self.logger.error(const.ERR_DEVICE_NOT_READY)
                    return(ResultCode.FAILED, const.ERR_SCAN)

            except DevFailed as dev_failed:
                log_msg = const.ERR_SCAN + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.ScanCommand()",
                                             tango.ErrSeverity.ERR)

    def is_Scan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """
        handler = self.get_command_object("Scan")
        return handler.check_allowed()

    @command(
        dtype_in=('str'),
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def Scan(self, argin):
        """Invoke Scan command to SDP subarray. """

        handler = self.get_command_object("Scan")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    class EndScanCommand(ResponseCommand):
        """
        A class for SdpSubarrayLeafNode's EndScan() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device
            state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: Exception if command execution throws any type of exception.

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("EndScan() is not allowed in current state",
                                             "Failed to invoke EndScan command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.EndScan()",
                                             tango.ErrSeverity.ERR)
            return True

        def endscan_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the endscan command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
            for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            It invokes EndScan command on SdpSubarray.
            This command is allowed when SdpSubarray is in SCANNING state.

            :param argin: None

            :return: A tuple containing a return code and a string message indicating status.
                     The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if the command execution is not successful.
            """
            device = self.target
            try:
                if device._sdp_subarray_proxy.obsState == ObsState.SCANNING:
                    device._sdp_subarray_proxy.command_inout_asynch(const.CMD_ENDSCAN,
                                                                    self.endscan_cmd_ended_cb)
                    device._read_activity_message = const.STR_ENDSCAN_SUCCESS
                    self.logger.info(const.STR_ENDSCAN_SUCCESS)
                    return(ResultCode.OK, const.STR_ENDSCAN_SUCCESS)
                else:
                    device._read_activity_message = const.ERR_DEVICE_NOT_IN_SCAN
                    self.logger.error(const.ERR_DEVICE_NOT_IN_SCAN)
                    return(ResultCode.FAILED, const.ERR_ENDSCAN_INVOKING_CMD)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ENDSCAN_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.EndScanCommand()",
                                             tango.ErrSeverity.ERR)

    def is_EndScan_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.
        :return: True if this command is allowed to be run in current device state.
        :rtype: boolean
        """

        handler = self.get_command_object("EndScan")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def EndScan(self):
        """
        Invokes EndScan on SdpSubarrayLeafNode.

        """
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class EndSBCommand(ResponseCommand):
        """
        A class for SdpSubarrayLeafNode's EndSB() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state.

            :return: True if this command is allowed to be run in current device state.

            :rtype: boolean

            :raises: Exception if command execution throws any type of exception.

            """
            if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("EndSB() is not allowed in current state",
                                             "Failed to invoke EndSB command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.EndSB()",
                                             tango.ErrSeverity.ERR)

            return True

        def endsb_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the endsb command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
            for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            This command invokes EndSB command on SDP subarray to end the current Scheduling block.

            :return: A tuple containing a return code and a string message indicating status.
                     The message is for information purpose only.

            :rtype: (ResultCode, str)

            :raises: DevFailed if the command execution is not successful.
            """
            device = self.target
            try:
                if device._sdp_subarray_proxy.obsState == ObsState.READY:
                    device._sdp_subarray_proxy.command_inout_asynch(const.CMD_RESET, self.endsb_cmd_ended_cb)
                    device._read_activity_message = const.STR_ENDSB_SUCCESS
                    self.logger.info(const.STR_ENDSB_SUCCESS)
                    return(ResultCode.OK, const.STR_ENDSB_SUCCESS)
                else:
                    device._read_activity_message = const.ERR_DEVICE_NOT_READY
                    self.logger.error(const.ERR_DEVICE_NOT_READY)
                    return(ResultCode.FAILED, const.ERR_DEVICE_NOT_READY)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ENDSB_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.EndSBCommand()",
                                             tango.ErrSeverity.ERR)

    def is_EndSB_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        """

        handler = self.get_command_object("EndSB")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def EndSB(self):
        """ This command invokes EndSB command on SDP subarray to end the current Scheduling block.
        """
        handler = self.get_command_object("EndSB")
        (result_code, message) = handler()
        return [[result_code], [message]]

    class AbortCommand(ResponseCommand):
        """
        A class for sdpSubarrayLeafNode's Abort() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [
                DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("Abort() is not allowed in current state",
                                             "Failed to invoke Abort command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.Abort()",
                                             tango.ErrSeverity.ERR)
            return True

        def abort_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the abort command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
            for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            Command to abort the current operation being done on the SDP subarray.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs while invoking command on CSPSubarray.

            """
            device = self.target
            try:
                if device._sdp_subarray_proxy.obsState in [ObsState.READY, ObsState.CONFIGURING,
                                                           ObsState.SCANNING,
                                                           ObsState.IDLE, ObsState.RESETTING]:
                    device._sdp_subarray_proxy.command_inout_asynch(const.CMD_ABORT, self.abort_cmd_ended_cb)
                    device._read_activity_message = const.STR_ABORT_SUCCESS
                    self.logger.info(const.STR_ABORT_SUCCESS)
                    return(ResultCode.OK, const.STR_ABORT_SUCCESS)

                else:
                    log_msg = ("Sdp Subarray is in ObsState {device._sdp_subarray_proxy.obsState.name}.""Unable to invoke Abort command")
                    device._read_activity_message = log_msg
                    self.logger.error(log_msg)
                    return(ResultCode.FAILED, log_msg)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ABORT_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.AbortCommand()",
                                             tango.ErrSeverity.ERR)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def Abort(self):
        """
        Invoke Abort on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("Abort")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_Abort_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Abort")
        return handler.check_allowed()

    class RestartCommand(ResponseCommand):
        """
        A class for sdpSubarrayLeafNode's Restart() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [
                DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("Restart() is not allowed in current state",
                                             "Failed to invoke Restart command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.Restart()",
                                             tango.ErrSeverity.ERR)

            return True

        def restart_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the restart command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
            for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            Command to restart the SDP subarray and bring it to its ON state.

            :return: A tuple containing a return code and a string message indicating status. The message is for
                        information purpose only.

            :rtype: (ReturnCode, str)

            :raises: DevFailed if error occurs while invoking command on SDPSubarray.

            """
            device = self.target
            try:
                if device._sdp_subarray_proxy.obsState in [ObsState.ABORTED, ObsState.FAULT]:
                    device._sdp_subarray_proxy.command_inout_asynch(const.CMD_RESTART,
                                                                    self.restart_cmd_ended_cb)
                    device._read_activity_message = const.STR_RESTART_SUCCESS
                    self.logger.info(const.STR_RESTART_SUCCESS)
                    return(ResultCode.OK, const.STR_RESTART_SUCCESS)

                else:
                    log_msg = "Sdp Subarray is in ObsState " + str(device._sdp_subarray_proxy.obsState) + \
                              ". Unable to invoke Restart command."
                    device._read_activity_message = log_msg
                    self.logger.error(log_msg)
                    return(ResultCode.FAILED, log_msg)

            except DevFailed as dev_failed:
                log_msg = const.ERR_RESTART_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.RestartCommand()",
                                             tango.ErrSeverity.ERR)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def Restart(self):
        """
        Invoke Restart command on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("Restart")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_Restart_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        handler = self.get_command_object("Restart")
        return handler.check_allowed()

    class ObsResetCommand(BaseCommand):
        """
        A class for SdpSubarrayLeafNode's ObsResetCommand() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            if self.state_model.op_state in [
                DevState.UNKNOWN, DevState.DISABLE,
            ]:
                tango.Except.throw_exception("ObsResetCommand() is not allowed in current state",
                                             "Failed to invoke ObsReset command on SdpSubarrayLeafNode.",
                                             "sdpsubarrayleafnode.ObsResetCommand()",
                                             tango.ErrSeverity.ERR)

            return True

        def obsreset_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the ObsResetCommand has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
            for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            Command to reset the SDP subarray and bring it to its RESETTING state.

            :param argin: None
            
            :return: None

            :raises: DevFailed if error occurs while invoking command on SDPSubarray.

            """
            device = self.target
            try:
                if device._sdp_subarray_proxy.obsState in [ObsState.ABORTED, ObsState.FAULT]:
                    device._sdp_subarray_proxy.command_inout_asynch(const.CMD_OBSRESET,
                                                                    self.obsreset_cmd_ended_cb)
                    device._read_activity_message = const.STR_OBSRESET_SUCCESS
                    self.logger.info(const.STR_OBSRESET_SUCCESS)

                else:
                    log_msg = "Sdp Subarray is in ObsState {} . Unable to invoke ObsReset command".format(str(device._sdp_subarray_proxy.obsState))
                    device._read_activity_message = log_msg
                    self.logger.error(log_msg)

            except DevFailed as dev_failed:
                log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                             "SdpSubarrayLeafNode.ObsResetCommand()",
                                             tango.ErrSeverity.ERR)

    @command(
    )
    @DebugIt()
    def ObsReset(self):
        """
        Invoke ObsReset command on SdpSubarrayLeafNode.
        """
        handler = self.get_command_object("ObsReset")
        handler()

    def is_ObsReset_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        """
        handler = self.get_command_object("ObsReset")
        return handler.check_allowed()

    class OnCommand(SKABaseDevice.OnCommand):
        """
        A class for SDP Subarray's On() command.
        """

        def on_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the On command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
                          callback model for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device = self.target
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
            log_msg = const.CMD_ON + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)
            return (ResultCode.OK, log_msg)

    class OffCommand(SKABaseDevice.OffCommand):
        """
        A class for SDP master's Off() command.
        """

        def off_cmd_ended_cb(self, event):
            """
            Callback function immediately executed when the asynchronous invoked command returns.
            Checks whether the off command has been successfully invoked on SDP Subarray.

            :param event: A CmdDoneEvent object.
            This class is used to pass data to the callback method in asynchronous callback model
            for command execution.

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
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                device._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device._read_activity_message = log
                self.logger.info(log)

        def do(self):
            """
            Sets the OperatingState to Off.

            :param argin: None.

            :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

            :rtype: (ResultCode, str)

            """
            device = self.target
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_OFF, self.off_cmd_ended_cb)
            self.logger.debug(const.STR_OFF_CMD_SUCCESS)
            device._read_activity_message = const.STR_OFF_CMD_SUCCESS
            return (ResultCode.OK, const.STR_OFF_CMD_SUCCESS)


# pylint: enable=unused-argument,unused-variable, implicit-str-concat

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpSubarrayLeafNode.main) ENABLED START #
    """
    Runs the SdpSubarrayLeafNode

    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: SdpSubarrayLeafNode TANGO object

    """
    return run((SdpSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.main


if __name__ == '__main__':
    main()
