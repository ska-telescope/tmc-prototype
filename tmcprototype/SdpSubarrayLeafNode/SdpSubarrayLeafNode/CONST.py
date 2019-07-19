# # In/Out command constants
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseResources"
CMD_CONFIGURE = "Configure"
#
# #Error messages
ERR_INIT_PROP_ATTR_CN = "Error on initialising properties and attributes " \
                         "on Sdp Subarray Leaf Node Node device."
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_RELEASE_RESOURCES_CMD = "Error occured while releasing resources "
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the SDP Subarray \n"
ERR_RELEASE_RESOURCES = "Error occurred while releasing resources from the Subarray \n"
ERR_CONFIGURE = "Error while invoking Configure command on SDP Subarray."
ERR_INVALID_JSON_CONFIG = "Invalid JSON format while invoking Configure command on SDP Subarray."
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
STR_CONFIG_EXEC = "Configure command execution"

#
STR_CMD_FAILED = "SDP Subarray Leaf Node_CommandFailed"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
#
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
#
# #INTEGERS
# INT_SKA_LEVEL = 1
