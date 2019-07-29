# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""
SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
It also acts as a SDP contact point for Subarray Node for observation execution.

"""

# PROTECTED REGION ID(SdpSubarrayLeafNode.additionnal_import) ENABLED START #
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpSubarrayLeafNode"
sys.path.insert(0, module_path)
# PyTango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, DeviceMeta, command, device_property, attribute
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
# Additional imports

from future.utils import with_metaclass
import CONST
import json

# PROTECTED REGION END #    //  SdpSubarrayLeafNode.additionnal_import

__all__ = ["SdpSubarrayLeafNode", "main"]


class SdpSubarrayLeafNode(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    SDP Subarray Leaf node is to monitor the SDP Subarray and issue control actions during an observation.
    """
    # __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SdpSubarrayLeafNode.class_variable) ENABLED START #

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on SDP Subarray.
        :param
            event: response from SDP Subarray for the invoked command
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
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------






    SdpSubarrayNodeFQDN = device_property(
        dtype='str', default_value="tango://dada:10000/mid_sdp/elt/subarray_1",
        doc='FQDN of the SDP Subarray Node Tango Device Server.',
    )

    # ----------
    # Attributes
    # ----------











    receiveAddresses = attribute(
        dtype='str',
        doc='This is a forwarded attribute from SDP Master which depicts State of the SDP.'
    )

    sdpSubarrayHealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
        doc='This is a forwarded attribute from SDP Subarray which depicts Health State of the SDP Subarray.',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc='String providing information about the current activity in SDP Subarray Leaf Node',
    )

    activeProcessingBlocks = attribute(
        dtype='str',
        doc='This is a forwarded attribute from SDP Subarray which depicts the active Processing Blocks in '
            'the SDP Subarray.',
    )

    sdpSubarrayHealthState = attribute(name="sdpSubarrayHealthState", label="sdpSubarrayHealthState", forwarded=True)

    sdpSubarrayObsState = attribute(name="sdpSubarrayObsState", label="sdpSubarrayObsState",forwarded=True)

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SdpSubarrayLeafNode.init_device) ENABLED START #
        """ Initializes the attributes and properties of the Central Node. """
        try:
            # Initialise device state
            self.set_state(DevState.ON) # set State=On
            # Initialise attributes
            self._receive_addresses = ""
            self._sdp_subarray_health_state = CONST.ENUM_OK
            self._read_activity_message = ""
            self._active_processing_block = ""
            # Initialise Device status
            self.set_status(CONST.STR_INIT_SUCCESS)
            # Create Device proxy for Sdp Subarray using SdpSubarrayNodeFQDN property
            self._sdp_subarray_proxy = DeviceProxy(self.SdpSubarrayNodeFQDN)
        except DevFailed as dev_failed:
            print(CONST.ERR_INIT_PROP_ATTR_CN)
            self._read_activity_message = CONST.ERR_INIT_PROP_ATTR_CN
            self.dev_logging(CONST.ERR_INIT_PROP_ATTR_CN, int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.STR_ERR_MSG + str(dev_failed)
            print(CONST.STR_ERR_MSG, dev_failed)

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
        """ Returns the Receive Addresses."""
        return self._receive_addresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.receiveAddresses_read

    def read_sdpSubarrayHealthState(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.sdpSubarrayHealthState_read) ENABLED START #
        """ Returns SDP Subarray Health State"""
        return self._sdp_subarray_health_state
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.sdpSubarrayHealthState_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_read) ENABLED START #
        """ Returns Activity Messages"""
        return self._read_activity_message
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_write) ENABLED START #
        """ Sets the Activity Message"""
        self._read_activity_message = value
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_write

    def read_activeProcessingBlocks(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activeProcessingBlocks_read) ENABLED START #
        """ Returns Active Processing Blocks"""
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
                Release all the resources of given Subarray. It accepts the subarray id, releaseALL flag and
                receptorIDList in JSON string format. When the releaseALL flag is True, ReleaseAllResources command
                is         invoked on the respective subarray. In this case, the receptorIDList tag is empty as all
                the resources of the Subarray are released.
                When releaseALL is False, ReleaseResources will be invoked on the Subarray and the resources provided
                in receptorIDList tag, are released from Subarray. This selective release of the resources when
                releaseALL is False, will be implemented in the later stages of the prototype.
                :param
                    argin: None
                :return:
                """
        excpt_msg = []
        excpt_count = 0

        try:

            # Call SDP Subarray Command asynchronously
            self.response = self._sdp_subarray_proxy.command_inout_asynch(CONST.CMD_RELEASE_RESOURCES,
                                                                          self.commandCallback)
            # Update the status of command execution status in activity message
            self._read_activity_message = CONST.STR_REL_RESOURCES
        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            # self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_RELEASE_RESOURCES + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_RELEASE_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_RELEASE_RESOURCES + str(except_occurred), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_RELEASE_RESOURCES + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_RELEASE_RES_EXEC, tango.ErrSeverity.ERR)

        return ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReleaseAllResources

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReleaseResources) ENABLED START #
        """
        Release resources
        :param
            argin: None
        :return:
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
        For PI#3 this command will be provided as a noop placeholder from SDP subarray.
        Eventually this will likely take a JSON string specifying the resource request.


        :param argin: The string in JSON format. The JSON contains following values:

            Processing Block ID List:
                Mandatory JSON object consisting of

                processingBlockIdList:
                    DevVarStringArray
                    The individual string should contain PB numbers in string format
                    with preceding zeroes upto 3 digits. E.g. 0001, 0002.

            Example:
                {
                "processingBlockIdList": ["0001", "0002"]
                }

        Note: From Jive, enter input as:
        {"processingBlockIdList": ["0001", "0002"]} without any space.

        :return: None
        """
        excpt_msg = []
        excpt_count = 0

        try:
            jsonArgument = json.loads(argin)
            processingBlockIDList = jsonArgument[CONST.STR_PROCESSINGBLOCKID_LIST]
            # Call SDP Subarray Command asynchronously
            self.response = self._sdp_subarray_proxy.command_inout_asynch(CONST.CMD_ASSIGN_RESOURCES,
                                                                          str(processingBlockIDList),
                                                                          self.commandCallback)
            # Update the status of command execution status in activity message
            self._read_activity_message = CONST.STR_ASSIGN_RESOURCES_SUCCESS
        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            # self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_ASSGN_RESOURCES + str(dev_failed), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_ASSGN_RESOURCES + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
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

        return ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.AssignResources

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Configure) ENABLED START #
        """ When commanded in the IDLE state: configures the Subarray device by providing the SDP PB configuration
        needed to execute the receive workflow

            :param argin: The string in JSON format. The JSON contains following values:

            Example:
            {
              "sdp": {
                "configure": {
                  "id": "realtime-20190627-0001",
                  "sbiId": "20190627-0001",
                  "workflow": {
                    "id": "vis_ingest",
                    "type": "realtime",
                    "version": "0.1.0"
                  },
                  "parameters": {
                    "numStations": 4,
                    "numChanels": 372,
                    "numPolarisations": 4,
                    "freqStartHz": 0.35e9,
                    "freqEndHz": 1.05e9,
                    "fields": {
                      "0": {
                        "system": "ICRS",
                        "name": "NGC6251",
                        "ra": 1.0,
                        "dec": 1.0
                      }
                    }
                  },
                  "scanParameters": {
                    "12345": {
                      "fieldId": 0,
                      "intervalMs": 1400
                    }
                  }
                },
                "configureScan": {
                  "scanParameters": {
                    "12346": {
                      "fieldId": 0,
                      "intervalMs": 2800
                    }
                  }
                }
              }
            }
        Note:
        from Jive, enter input as :
        {"sdp":{"configure":{"id":"realtime-20190627-0001","sbiId":"20190627-0001","workflow":
        {"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":{"numStations":4,"numChanels":372,
        "numPolarisations":4,"freqStartHz":0.35e9,"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":
        "NGC6251","ra":1.0,"dec":1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},
        "configureScan":{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}

        :return: None.
        """
        excpt_msg = []
        excpt_count = 0
        try:
            # TODO : Check if obsState == IDLE
            jsonArgument = json.loads(argin)
            configure_arg = jsonArgument["sdp"]["configure"]
            self._sdp_subarray_proxy.command_inout_asynch(CONST.CMD_CONFIGURE, str(configure_arg), self.commandCallback)
            self._read_activity_message = CONST.STR_CONFIGURE_SUCCESS
            self.dev_logging(CONST.STR_CONFIGURE_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON_CONFIG + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON_CONFIG + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            # self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_CONFIGURE + str(dev_failed),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_CONFIGURE + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_CONFIGURE + str(except_occurred),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_CONFIGURE + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_CONFIG_EXEC, tango.ErrSeverity.ERR)



        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Configure

    @command(
    dtype_in='str',
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Scan) ENABLED START #
        """
        Send Scan command to SDP subarray.

        :param argin: The JSON string format. The string contains following values:

            Example: {"scan_duration":0}

        Note: From Jive, enter input as:
        {"scan_duration":0} without any space.

        """
        excpt_msg = []
        excpt_count = 0

        try:
            # TODO : No use of scan_duration as Sdp Subarray does not accept any arguments.
            jsonArgument = json.loads(argin)
            scan_duration = jsonArgument["scan_duration"]
            sdp_subarray_obs_state = self._sdp_subarray_proxy.obsState
            # Check if SDP Subarray obsState is READY
            if sdp_subarray_obs_state == CONST.ENUM_READY:
                self._sdp_subarray_proxy.command_inout_asynch(CONST.CMD_SCAN,list(str(scan_duration)),self.commandCallback)
                self._read_activity_message = CONST.STR_SCAN_SUCCESS
                self.dev_logging(CONST.STR_SCAN_SUCCESS, int(tango.LogLevel.LOG_INFO))
        except ValueError as value_error:
            self.dev_logging(CONST.ERR_INVALID_JSON_SCAN + str(value_error), int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_INVALID_JSON_SCAN + str(value_error)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except KeyError as key_error:
            self.dev_logging(CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error), int(tango.LogLevel.LOG_ERROR))
            # self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self._read_activity_message = CONST.ERR_JSON_KEY_NOT_FOUND
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1
        except DevFailed as dev_failed:
            self.dev_logging(CONST.ERR_SCAN + str(dev_failed),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_SCAN + str(dev_failed)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        except Exception as except_occurred:
            self.dev_logging(CONST.ERR_SCAN + str(except_occurred),
                             int(tango.LogLevel.LOG_ERROR))
            self._read_activity_message = CONST.ERR_SCAN + str(except_occurred)
            excpt_msg.append(self._read_activity_message)
            excpt_count += 1

        # throw exception:
        if excpt_count > 0:
            err_msg = ' '
            for item in excpt_msg:
                err_msg += item + "\n"
            tango.Except.throw_exception(CONST.STR_CMD_FAILED, err_msg,
                                         CONST.STR_SCAN_EXEC, tango.ErrSeverity.ERR)

    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Scan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.EndScan) ENABLED START #
        """
        It invokes 'EndScan' command on SdpSubarray. This command is allowed when SdpSubarray is in SCANNING
        state

        :return : None
        """

        excpt_msg = []
        excpt_count = 0
        try:
            if self._sdp_subarray_proxy.obsState == CONST.ENUM_SCANNING:
                self._sdp_subarray_proxy.command_inout_asynch(CONST.CMD_ENDSCAN, self.commandCallback)
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
            self.dev_logging(CONST.ERR_ENDSCAN_INVOKING_CMD + str(except_occurred), int(tango.LogLevel.LOG_ERROR))
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

        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.EndSB) ENABLED START #
        """ Ends Scheduling block"""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.EndSB

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Abort) ENABLED START #
        """ Abort command"""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Abort

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
