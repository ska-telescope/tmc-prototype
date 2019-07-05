# In/Out command constants
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseAllResources"
CMD_ADD_RECEPTORS = "AddReceptors"
CMD_REMOVE_ALL_RECEPTORS = "RemoveAllReceptors"

#Event messages
EVT_SUBSR_SA_RECEPTOR_ID_LIST = "receptorIDList"

#Error messages
ERR_IN_CREATE_PROXY = "Error in creating proxy of the LeafNode device: "
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_RELEASE_RESOURCES_CMD = "Error occured while releasing resources "
ERR_SUBARRAY_HEALTHSTATE = "Key Error occurred while setting Subarray healthState"
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the Subarray \n"
ERR_RELEASE_RESOURCES = "Error occurred while releasing resources from the Subarray \n"
ERR_STOW_ARGIN = "Invalid StowAntennas arguments \n"
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_INIT_PROP_ATTR_CSPSALN = "Error on initialising properties and attributes " \
                        "on CspSubarrayLeaf Node device."

#strings
#General strings
STR_RECEPTORID_LIST = "receptorIDList"
STR_DISH = "dish"

STR_HEALTH_STATE = "healthState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_ERR_MSG = "Error message is: "
STR_INIT_SUCCESS = "CspSubarrayLeafNode is initialized successfully."
STR_FALSE = "False"
STR_ASSIGN_RESOURCES_SUCCESS = "Resources are assigned successfully"
STR_RELEASE_ALL_RESOURCES_SUCCESS = "All resources are removed successfully"
STR_CSP_CBF_DEV_NAME = "mid_csp_cbf/sub_elt/master"
STR_CSPSALN_INIT_SUCCESS = "CspSubarrayLeafNode initialized successfully."
STR_CMD_FAILED = "CspSubarrayLeafNode_CommandFailed"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_INVOKE_SUCCESS = " invoked successfully."
STR_COMMAND = "Command :-> "
STR_CMD_FAILED = "CspSubarrayLeafNode Commandfailed"
STR_CMD_CALLBK = "CspSubarrayLeafNode Command Callback"
STR_FALSE = "False"
PROP_DEF_VAL_CSP_MID_SA1 = "mid-csp/elt/subarray01"

ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = list(range(0, 4))
ENUM_INIT, ENUM_OFF, ENUM_ON, ENUM_ALARM, ENUM_DISABLE, ENUM_FAULT, ENUM_UNKNOWN = list(range(0, 7))

#INTEGERS
INT_SKA_LEVEL = 3