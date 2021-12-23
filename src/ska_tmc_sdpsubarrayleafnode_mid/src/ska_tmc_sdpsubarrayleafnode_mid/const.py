# # In/Out command constants
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseResources"
CMD_CONFIGURE = "Configure"
CMD_SCAN = "Scan"
CMD_ENDSCAN = "EndScan"
CMD_END = "End"
CMD_ABORT = "Abort"
CMD_RESTART = "Restart"
CMD_OBSRESET = "ObsReset"
CMD_TELESCOPE_ON = "TelescopeOn"
CMD_TELESCOPE_OFF = "TelescopeOff"
CMD_ON = "On"
CMD_OFF = "Off"
CMD_RESET = "Reset"


# #Error messages
ERR_INIT_PROP_ATTR_CN = (
    "Error on initialising properties and attributes "
    "on Sdp Subarray Leaf Node Node device."
)
ERR_INVALID_JSON = "Invalid JSON format"
ERR_RESET_INVOKING_CMD = (
    "Error while invoking Reset command on SDP SubarrayLeafNode."
)
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_ENDSCAN_INVOKING_CMD = (
    "Error while invoking EndScan command on SDP Subarray."
)
ERR_END_INVOKING_CMD = "Error while invoking End command on SDP Subarray."
ERR_ABORT_INVOKING_CMD = "Error while invoking Abort command on SDP Subarray."
ERR_RESTART_INVOKING_CMD = (
    "Error while invoking Restart command on SDP Subarray."
)
ERR_OBSRESET_INVOKING_CMD = (
    "Error while invoking ObsReset command on SDP Subarray."
)
ERR_ASSGN_RESOURCES = (
    "Error occurred while assigning resources to the SDP Subarray \n"
)
ERR_RELEASE_RESOURCES = (
    "Error occurred while releasing resources from the Subarray \n"
)
ERR_CONFIGURE = "Error while invoking Configure command on SDP Subarray."
ERR_SCAN = "Error while invoking Scan command on SDP Subarray."
ERR_INVOKING_TELESCOPE_ON_CMD = (
    "Error while invoking TelescopeOn command on SDP Subarray."
)
ERR_INVOKING_TELESCOPE_OFF_CMD = (
    "Error while invoking TelescopeOff command on SDP Subarray."
)
ERR_INVOKING_ON_CMD = "Error while invoking On command on SDP Subarray."
ERR_INVOKING_OFF_CMD = "Error while invoking Off command on SDP Subarray."
ERR_INVALID_JSON_CONFIG = (
    "Invalid JSON format while invoking Configure command on SDP Subarray."
)
ERR_INVALID_JSON_SCAN = (
    "Invalid JSON format while invoking Scan command on SDP Subarray."
)
ERR_UNABLE_RESET_CMD = "Unable to invoke Reset command"
ERR_DEVICE_NOT_IN_SCAN = "SdpSubarray is not in SCANNING state."
ERR_DEVICE_NOT_IN_EMPTY_IDLE = "SdpSubarray is not in EMPTY/IDLE state."
ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_EXCEPT_RELEASE_ALL_RESOURCES_CMD_CB = (
    "Exception in ReleaseAllResources CommandCallback: \n"
)
ERR_EXCEPT_CONFIGURE_CMD_CB = "Exception in Configure CommandCallback: \n"
ERR_EXCEPT_SCAN_CMD_CB = "Exception in Scan CommandCallback: \n"
ERR_EXCEPT_END_SCAN_CMD_CB = "Exception in EndScan CommandCallback: \n"
ERR_EXCEPT_END_SB_CMD_CB = "Exception in End CommandCallback: \n"
ERR_EXCEPT_ABORT_CMD_CB = "Exception in Abort CommandCallback: \n"
ERR_EXCEPT_RESTART_CMD_CB = "Exception in Restart CommandCallback: \n"
ERR_EXCEPT_ON_CMD_CB = "Exception in On CommandCallback: \n"
ERR_EXCEPT_OFF_CMD_CB = "Exception in Off CommandCallback: \n"
ERR_DEVICE_NOT_READY = "SdpSubarray is not in ready state."
ERR_DEVICE_NOT_EMPTY_OR_IDLE = "SdpSubarray is not in EMPTY/IDLE state."
ERR_DEVICE_NOT_READY_IDLE = "SdpSubarray is not in ready or idle state."
ERR_DEVICE_NOT_READY_IDLE_CONFIG_SCAN_RESET = "SdpSubarray is not in configuring, scanning, resetting, ready or idle state."
ERR_DEVICE_NOT_ABORTED_FAULT = "SdpSubarray is not in aborted or fault state."
ERR_DEVICE_NOT_READY_OR_IDLE = "SDP subarray is not in READY or IDLE obsState."
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_IN_CREATE_PROXY_SDPSA = (
    "Error in creating proxy of the SDP Subarray device."
)
ERR_CMD_FAILED = "SdpSubarrayLeafNode_Commandfailed in callback"


# #strings
# #General strings
STR_HEALTH_STATE = "healthState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = (
    "SDP Subarray leaf healthState event returned unknown value \n"
)
STR_ERR_MSG = "Error message is: "
STR_RESET_SUCCESS = (
    "Reset command is invoked successfully on SDP SubarrayLeafNode."
)
STR_INIT_SUCCESS = "SDP Subarray Leaf Node is initialized successfully."
STR_FALSE = "False"
STR_SDPSALN_INIT_SUCCESS = "SdpSubarrayLeafNode initialized successfully."
STR_PROCESSINGBLOCKID_LIST = "processingBlockIdList"
STR_ASSIGN_RESOURCES_SUCCESS = "Resources are assigned successfully"
STR_FALSE_TAG = "False in ReleaseALL tag is not yet supported"
STR_REL_RESOURCES = "Release Resources invoked successfully on SDP Subarray."
STR_ALL_RES_NOT_REL = "All the resources are not released"
STR_LIST_RES_NOT_REL = "List of the resources that are not released:"
STR_CONFIGURE_SUCCESS = "Configure invoked successfully on SdpSubarray."
STR_ENDSCAN_SUCCESS = "EndScan invoked successfully on SdpSubarray."
STR_END_SUCCESS = "End invoked successfully on SdpSubarray."
STR_CONFIG_EXEC = "Configure command execution"
STR_SCAN_EXEC = "Scan command execution"
STR_ENDSCAN_EXEC = "Endscan command execution"
STR_END_EXEC = "End command execution"
STR_ABORT_EXEC = "Abort command execution"
STR_RESTART_EXEC = "Restart command execution"
STR_OBSRESET_EXEC = "ObsReset command execution"
STR_TELESCOPE_ON_EXEC = "TelescopeOn command execution"
STR_TELESCOPE_OFF_EXEC = "TelescopeOff command execution"
STR_OFF_EXEC = "Off command execution"
STR_RESET_EXEC = "Reset command execution"
STR_ON_EXEC = "On command execution"
STR_ABORT_SUCCESS = "Abort invoked successfully on SdpSubarray."
STR_RESTART_SUCCESS = "Restart invoked successfully on SdpSubarray."
STR_OBSRESET_SUCCESS = "ObsReset invoked successfully on SdpSubarray."
STR_SCAN_EXEC = "Scan command execution"
STR_SCAN_SUCCESS = "Scan invoked successfully on SdpSubarray."
STR_CMD_FAILED = "SDP Subarray Leaf Node_CommandFailed"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_ENDSCAN_EXEC = "EndScan command execution"
STR_END_EXEC = "End command execution"
STR_RELEASE_RES_CMD_CALLBK = (
    "SdpSubarrayLeafNode ReleaseAllresources Command Callback"
)
STR_CONFIGURE_CMD_CALLBK = "SdpSubarrayLeafNode Configure Command Callback"
STR_SCAN_CMD_CALLBK = "SdpSubarrayLeafNode Scan Command Callback"
STR_ENDSCAN_CMD_CALLBK = "SdpSubarrayLeafNode EndScan Command Callback"
STR_END_CMD_CALLBK = "SdpSubarrayLeafNode End Command Callback"
STR_ABORT_CMD_CALLBK = "SdpSubarrayLeafNode Abort Command Callback"
STR_RESTART_CMD_CALLBK = "SdpSubarrayLeafNode Restart Command Callback"
STR_ON_CALLBK = "SdpSubarrayLeafNode On Command Callback"
STR_OFF_CALLBK = "SdpSubarrayLeafNode Off Command Callback"
STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = " invoked successfully."
STR_OFF_CMD_SUCCESS = "Off command executed successfully."
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "

# #PROPERTIES DEFAULT VALUES
PROP_DEF_VAL_TM_MID_SDP_SA = "mid_sdp/elt/subarray_1"
