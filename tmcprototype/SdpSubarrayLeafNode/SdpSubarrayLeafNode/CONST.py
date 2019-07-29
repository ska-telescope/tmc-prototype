# # In/Out command constants
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseResources"
CMD_CONFIGURE = "Configure"
CMD_SCAN = "Scan"
CMD_ENDSCAN = "EndScan"
#
# #Error messages
ERR_INIT_PROP_ATTR_CN = "Error on initialising properties and attributes " \
                         "on Sdp Subarray Leaf Node Node device."
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_RELEASE_RESOURCES_CMD = "Error occured while releasing resources "
ERR_ENDSCAN_INVOKING_CMD = "Error while invoking EndScan command on SDP Subarray."
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the SDP Subarray \n"
ERR_RELEASE_RESOURCES = "Error occurred while releasing resources from the Subarray \n"
ERR_CONFIGURE = "Error while invoking Configure command on SDP Subarray."
ERR_SCAN = "Error while invoking Scan command on SDP Subarray."
ERR_INVALID_JSON_CONFIG = "Invalid JSON format while invoking Configure command on SDP Subarray."
ERR_INVALID_JSON_SCAN = "Invalid JSON format while invoking Scan command on SDP Subarray."
ERR_DEVICE_NOT_IN_SCAN = "SdpSubarray is not in SCANNING state."
#
# #strings
# #General strings
STR_HEALTH_STATE = "healthState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = "SDP Subarray leaf healthState event returned unknown value \n"
STR_ERR_MSG = "Error message is: "
STR_INIT_SUCCESS = "SDP Subarray Leaf Node is initialized successfully."
STR_FALSE = "False"
STR_PROCESSINGBLOCKID_LIST = "processingBlockIdList"
STR_ASSIGN_RESOURCES_SUCCESS = "Resources are assigned successfully"
STR_FALSE_TAG = "False in ReleaseALL tag is not yet supported"
STR_REL_RESOURCES = "Resources have been released successfully"
STR_ALL_RES_NOT_REL = "All the resources are not released"
STR_LIST_RES_NOT_REL = "List of the resources that are not released:"
STR_CONFIGURE_SUCCESS = "Configure invoked successfully on SdpSubarray."
STR_ENDSCAN_SUCCESS = "EndScan invoked successfully on SdpSubarray."
STR_CONFIG_EXEC = "Configure command execution"
STR_SCAN_EXEC = "Scan command execution"
STR_SCAN_SUCCESS = "Scan invoked successfully on SdpSubarray."

#
STR_CMD_FAILED = "SDP Subarray Leaf Node_CommandFailed"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_ENDSCAN_EXEC = "EndScan command execution"

# #PROPERTIES DEFAULT VALUES
PROP_DEF_VAL_TM_MID_SDP_SA = "mid_sdp/elt/subarray_1"
#
#
# ENUM_LAB_OK = "OK"
# ENUM_LAB_DEGRADED = "DEGRADED"
# ENUM_LAB_FAILED = "FAILED"
# ENUM_LAB_UNKNOWN = "UNKNOWN"
#
# #ENUMS
ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = list(range(0, 4))
ENUM_IDLE, ENUM_CONFIGURING, ENUM_READY, ENUM_SCANNING = list(range(0, 4))
#
# #INTEGERS
# INT_SKA_LEVEL = 1
