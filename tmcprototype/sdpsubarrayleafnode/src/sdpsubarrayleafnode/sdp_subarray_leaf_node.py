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
from tango.server import run,command, device_property, attribute
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState
# Additional imports
import json
from . import const

# PROTECTED REGION END #    //  SdpSubarrayLeafNode.additionnal_import

__all__ = ["SdpSubarrayLeafNode", "main"]

# pylint: disable=unused-argument,unused-variable
class SdpSubarrayLeafNode(SKABaseDevice):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
    """
    # __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SdpSubarrayLeafNode.class_variable) ENABLED START #

    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on SDP Subarray.

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
        try:
            if event.err:
                log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self._read_activity_message = log
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.logger.info(log)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                exception_message, exception_count, const.ERR_EXCEPT_CMD_CB)

        # Throw Exception
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_CMD_CALLBK)

    # Throw exceptions
    def _handle_devfailed_exception(self, df, except_msg_list, exception_count, read_actvity_msg):
        log_msg = read_actvity_msg + str(df)
        self.logger.error(log_msg)
        self._read_activity_message = read_actvity_msg + str(df)
        except_msg_list.append(self._read_activity_message)
        exception_count += 1
        return [except_msg_list, exception_count]

    def _handle_generic_exception(self, exception, except_msg_list, exception_count, read_actvity_msg):
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

    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.class_variable

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

    def init_device(self):
        """ Initializes the attributes and properties of the Central Node. """
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SdpSubarrayLeafNode.init_device) ENABLED START #
        try:
            # Initialise device state
            self.set_state(DevState.ON) # set State=On
            self.set_status(const.STR_SDPSALN_INIT_SUCCESS)
            # Initialise attributes
            self._receive_addresses = ""
            self._sdp_subarray_health_state = HealthState.OK
            self._read_activity_message = ""
            self._active_processing_block = ""
            # Initialise Device status
            self.set_status(const.STR_SDPSALN_INIT_SUCCESS)
            log_msg = const.STR_SDPSALN_INIT_SUCCESS
            self.logger.info(log_msg)
            self._read_activity_message = log_msg

            # Create Device proxy for Sdp Subarray using SdpSubarrayFQDN property
            self._sdp_subarray_proxy = DeviceProxy(self.SdpSubarrayFQDN)
        except DevFailed as dev_failed:
            self.logger.error(const.ERR_INIT_PROP_ATTR_CN)
            self._read_activity_message = const.ERR_INIT_PROP_ATTR_CN
            self.logger.error(const.ERR_INIT_PROP_ATTR_CN)
            self._read_activity_message = const.STR_ERR_MSG + str(dev_failed)
            self.logger.error(const.STR_ERR_MSG, dev_failed)

        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.init_device

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


    # --------
    # Commands
    # --------
    @command(
    )
    @DebugIt()
    def ReleaseAllResources(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReleaseAllResources) ENABLED START #
        """
        Releases all the resources of given Subarray. It accepts the subarray id, releaseALL flag and
        receptorIDList in JSON string format. When the releaseALL flag is True, ReleaseAllResources command
        is invoked on the respective subarray. In this case, the receptorIDList tag is empty as all the
        resources of the Subarray are released. When releaseALL is False, ReleaseResources will be invoked
        on the Subarray and the resources provided in receptorIDList tag, are released from Subarray.
        This selective release of the resources when releaseALL is False, will be implemented in the
        later stages of the prototype.

        :param argin: None.

        :return: None.
        """

        exception_message = []
        exception_count = 0

        try:
            # Call SDP Subarray Command asynchronously
            self.response = self._sdp_subarray_proxy.command_inout_asynch(const.CMD_RELEASE_RESOURCES,
                                                                          self.cmd_ended_cb)

            # Update the status of command execution status in activity message
            self._read_activity_message = const.STR_REL_RESOURCES
            self.logger.info(const.STR_REL_RESOURCES)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_RELEASE_RESOURCES)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                            exception_message, exception_count, const.ERR_RELEASE_RESOURCES)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_RELEASE_RES_EXEC)

        return ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReleaseAllResources

    @command(
        dtype_in='str',
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReleaseResources) ENABLED START #
        """
        This command results into selective release of the resources from
        SDP Subarray. This command is yet to be implemented.
        """
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReleaseResources

    @command(
        dtype_in='str',
        dtype_out='str',
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.AssignResources) ENABLED START #
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
                "coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min":0.35e9,
                "freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",
                "coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:57:22.9","subbands":[{"freq_min":0.35e9,
                "freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],"processing_blocks":[{
                "id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},
                "parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_realtime",
                "version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch",
                "id":"ical","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001",
                "type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb",
                "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":
                ["calibration"]}]}]}

            Note: Enter input without spaces

        :return: Empty String.
        """
        exception_message = []
        exception_count = 0

        try:
            # Call SDP Subarray Command asynchronously
            log_msg = "Input JSON for SDP Subarray Leaf Node AssignResource command is: " + argin
            self.logger.debug(log_msg)
            self.response = self._sdp_subarray_proxy.command_inout_asynch(const.CMD_ASSIGN_RESOURCES,
                                                                          argin, self.cmd_ended_cb)
            # Update the status of command execution status in activity message
            self._read_activity_message = const.STR_ASSIGN_RESOURCES_SUCCESS
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON + str(value_error)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1

        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_ASSGN_RESOURCES)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                            exception_message, exception_count,const.ERR_ASSGN_RESOURCES)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_ASSIGN_RES_EXEC)

        return ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.AssignResources

    @command(
        dtype_in='str',
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Configure) ENABLED START #
        """ When commanded in the IDLE state: configures the Subarray device by providing the SDP PB
        configuration needed to execute the receive workflow

        :param argin: The string in JSON format. The JSON contains following values:

        Example:

        {"sdp":{ "scan_type": "science_A" }}

        :return: None.
        """
        exception_message = []
        exception_count = 0
        try:
            # TODO : Check if obsState == IDLE
            # TODO : For future reference set toggleReadCbfOutLink to false to skip CbfOutLink validation
            # self._sdp_subarray_proxy.toggleReadCbfOutLink = False
            jsonArgument = json.loads(argin)
            sdp_arg = jsonArgument["sdp"]
            sdpConfiguration = sdp_arg.copy()
            log_msg = "Input JSON for SDP Subarray Leaf Node Configure command is: " + argin
            self.logger.debug(log_msg)
            self._sdp_subarray_proxy.command_inout_asynch(const.CMD_CONFIGURE, json.dumps(sdpConfiguration),
                                                          self.cmd_ended_cb)
            self._read_activity_message = const.STR_CONFIGURE_SUCCESS
            self.logger.debug(str(sdpConfiguration))
            self.logger.info(const.STR_CONFIGURE_SUCCESS)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON_CONFIG + str(value_error)
            self.logger.info(log_msg)
            self._read_activity_message = const.ERR_INVALID_JSON_CONFIG + str(value_error)
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except KeyError as key_error:
            log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.error(log_msg)
            self._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND
            exception_message.append(self._read_activity_message)
            exception_count += 1
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                                    exception_message, exception_count, const.ERR_CONFIGURE)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                    exception_message, exception_count,const.ERR_CONFIGURE)
        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_CONFIG_EXEC)

        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Configure

    @command(
        dtype_in='str',
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Scan) ENABLED START #
        """ Invoke Scan command to SDP subarray.

            :param argin: The string in JSON format. The JSON contains following values:
            Example:
            {“id”:1}.

            Note: Enter input as without spaces:{“id”:1}

            :return: None.
        """
        exception_message = []
        exception_count = 0
        try:
            sdp_subarray_obs_state = self._sdp_subarray_proxy.obsState
            # Check if SDP Subarray obsState is READY
            if sdp_subarray_obs_state == ObsState.READY:
                # TODO : Pass id as a string argument to sdp Subarray Scan command

                log_msg = "Input JSON for SDP Subarray Leaf Node Scan command is: " + argin
                self.logger.debug(log_msg)
                self._sdp_subarray_proxy.command_inout_asynch(const.CMD_SCAN, argin, self.cmd_ended_cb)
                self._read_activity_message = const.STR_SCAN_SUCCESS
                self.logger.info(const.STR_SCAN_SUCCESS)

            else:
                self._read_activity_message = const.ERR_DEVICE_NOT_READY
                self.logger.error(const.ERR_DEVICE_NOT_READY)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                                        exception_message, exception_count, const.ERR_SCAN)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                                        exception_message, exception_count, const.ERR_SCAN)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_SCAN_EXEC)

    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Scan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.EndScan) ENABLED START #
        """
        It invokes EndScan command on SdpSubarray. This command is allowed when SdpSubarray is in
        SCANNING state.

                        :param argin: None.

                        :return: None.
                        """

        exception_message = []
        exception_count = 0
        try:
            if self._sdp_subarray_proxy.obsState == ObsState.SCANNING:
                self._sdp_subarray_proxy.command_inout_asynch(const.CMD_ENDSCAN, self.cmd_ended_cb)
                self._read_activity_message = const.STR_ENDSCAN_SUCCESS
                self.logger.info(const.STR_ENDSCAN_SUCCESS)
            else:
                self._read_activity_message = const.ERR_DEVICE_NOT_IN_SCAN
                self.logger.error(const.ERR_DEVICE_NOT_IN_SCAN)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                        exception_message, exception_count, const.ERR_ENDSCAN_INVOKING_CMD)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                        exception_message, exception_count, const.ERR_ENDSCAN_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_ENDSCAN_EXEC)

        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.EndSB) ENABLED START #
        """ This command invokes EndSB command on SDP subarray to
         end the current Scheduling block."""

        # TODO: For future use
        exception_message = []
        exception_count = 0
        try:
            if self._sdp_subarray_proxy.obsState == ObsState.READY:
                # TODO : Instead of calling EndSB command, call Reset command here. cmdName = Reset, Add this in const.py
                self._sdp_subarray_proxy.command_inout_asynch(const.CMD_RESET, self.cmd_ended_cb)
                self._read_activity_message = const.STR_ENDSB_SUCCESS
                self.logger.info(const.STR_ENDSB_SUCCESS)
            else:
                self._read_activity_message = const.ERR_DEVICE_NOT_READY
                self.logger.error(const.ERR_DEVICE_NOT_READY)
        except DevFailed as dev_failed:
            [exception_message, exception_count] = self._handle_devfailed_exception(dev_failed,
                                            exception_message, exception_count, const.ERR_ENDSB_INVOKING_CMD)
        except Exception as except_occurred:
            [exception_message, exception_count] = self._handle_generic_exception(except_occurred,
                                        exception_message, exception_count, const.ERR_ENDSB_INVOKING_CMD)

        # throw exception:
        if exception_count > 0:
            self.throw_exception(exception_message, const.STR_ENDSB_EXEC)

        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.EndSB

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Abort) ENABLED START #
        """ Abort command. Not yet implememnted."""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Abort

# pylint: enable=unused-argument,unused-variable
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpSubarrayLeafNode.main) ENABLED START #
    """
    Runs the SdpSubarrayLeafNode.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: SdpSubarrayLeafNode TANGO object.
    """
    return run((SdpSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.main

if __name__ == '__main__':
    main()
