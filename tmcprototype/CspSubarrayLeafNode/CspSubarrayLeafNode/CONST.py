"""
CONST file for CspSubarrayLeafNode
"""
# In/Out command constants
CMD_ADD_RECEPTORS = "AddReceptors"
CMD_REMOVE_ALL_RECEPTORS = "RemoveAllReceptors"
CMD_CONFIGURESCAN = "ConfigureScan"

#Event messages
EVT_SUBSR_SA_RECEPTOR_ID_LIST = "receptorIDList"

#Error messages
ERR_IN_CREATE_PROXY = "Error in creating proxy of the LeafNode device: "
ERR_INVALID_JSON = "Invalid JSON format while invoking command on CspSubarray."
ERR_JSON_KEY_NOT_FOUND = "JSON key not found."
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the Csp Subarray \n"
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_INIT_PROP_ATTR_CSPSALN = "Error on initialising properties and attributes " \
                        "on CspSubarrayLeaf Node device."
ERR_MSG = "Error message is: "
ERR_RELEASE_ALL_RESOURCES = "Error while invoking ReleaseAllResources command on CSP Subarray."
ERR_CONFIGURESCAN_RESOURCES = "Error while invoking ConfigureScan command on CSP Subarray."
ERR_INVALID_JSON_CONFIG_SCAN = "Invalid JSON format while invoking ConfigureScan command on CspSubarray."
ERR_INVALID_JSON_ASSIGN_RES = "Invalid JSON format while invoking AddReceptors command on CspSubarray."

#strings
#General strings
STR_RECEPTORID_LIST = "receptorIDList"
STR_DISH = "dish"
STR_ERR_MSG = "Error message is: "
STR_ADD_RECEPTORS_SUCCESS = "Resources are assigned successfully on CspSubarray."
STR_REMOVE_ALL_RECEPTORS_SUCCESS = "All resources assigned to CSP Subarray are removed successfully."
STR_CONFIGURESCAN_SUCCESS = "ConfigureScan invoked successfully on CspSubarray."
STR_CSPSALN_INIT_SUCCESS = "CspSubarrayLeafNode initialized successfully."
STR_CMD_FAILED = "CspSubarrayLeafNode_CommandFailed"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_CONFIG_SCAN_EXEC = "ConfigureScan command execution"
STR_INVOKE_SUCCESS = " invoked successfully."
STR_COMMAND = "Command :-> "
STR_CMD_FAILED = "CspSubarrayLeafNode Commandfailed"
STR_CMD_CALLBK = "CspSubarrayLeafNode Command Callback"
STR_FALSE = "False"
PROP_DEF_VAL_CSP_MID_SA1 = "mid-csp/elt/subarray01"

STR_CSPSA_FQDN = "CspSubarrayNodeFQDN :-> "

ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = list(range(0, 4))
ENUM_INIT, ENUM_OFF, ENUM_ON, ENUM_ALARM, ENUM_DISABLE, ENUM_FAULT, ENUM_UNKNOWN = list(range(0, 7))

#INTEGERS
INT_SKA_LEVEL = 3
