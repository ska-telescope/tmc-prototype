"""
const file for CspSubarrayLeafNode
"""
# In/Out command constants
CMD_ADD_RECEPTORS = "AddReceptors"
CMD_REMOVE_ALL_RECEPTORS = "RemoveAllReceptors"
CMD_ENDSCAN = "EndScan"
CMD_CONFIGURE = "Configure"
CMD_STARTSCAN = "Scan"
CMD_GOTOIDLE = "GoToIdle"

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
ERR_CONFIGURE_INVOKING_CMD = "Error while invoking Configure command on CSP Subarray."
ERR_ENDSCAN_INVOKING_CMD = "Error while invoking EndScan command on CSP Subarray."
ERR_INVALID_JSON_CONFIG = "Invalid JSON format while invoking Configure command on CspSubarray."
ERR_INVALID_JSON_ASSIGN_RES = "Invalid JSON format while invoking AddReceptors command on CspSubarray."
ERR_STARTSCAN_RESOURCES = "Error while invoking StartScan command on CSP Subarray."
ERR_DEVICE_NOT_READY = "Csp subarray is not in ready state."
ERR_DEVICE_NOT_IN_SCAN = "CspSubarray is not in SCANNING state."
ERR_GOTOIDLE_INVOKING_CMD = "Error while invoking GoToIdle command on CSP Subarray."
ERR_IN_CREATE_PROXY_CSPSA = "Error in creating proxy of the CSP Subarray device."

#strings
#General strings
STR_RECEPTORID_LIST = "receptorIDList"
STR_DISH = "dish"
STR_ERR_MSG = "Error message is: "
STR_ADD_RECEPTORS_SUCCESS = "Resources are assigned successfully on CspSubarray."
STR_REMOVE_ALL_RECEPTORS_SUCCESS = "All resources assigned to CSP Subarray are removed successfully."
STR_CONFIGURE_SUCCESS = "Configure command invoked successfully on CspSubarray from " \
                            "CspSubarrayLeafNode."
STR_ENDSCAN_SUCCESS = "EndScan command invoked successfully on CspSubarray from CspSubarrayLeafNode."
STR_CSPSALN_INIT_SUCCESS = "CspSubarrayLeafNode initialized successfully."
STR_CMD_FAILED = "CspSubarrayLeafNode_CommandFailed"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_CONFIG_EXEC = "Configure command execution"
STR_ENDSCAN_EXEC = "EndScan command execution"
STR_INVOKE_SUCCESS = " invoked successfully."
STR_COMMAND = "Command :-> "
STR_CMD_FAILED = "CspSubarrayLeafNode Commandfailed"
STR_CMD_CALLBK = "CspSubarrayLeafNode Command Callback"
STR_FALSE = "False"
STR_STARTSCAN_SUCCESS = "Scan command is executed successfully."
PROP_DEF_VAL_CSP_MID_SA1 = "mid_csp/elt/subarray_01"
STR_START_SCAN_EXEC = "StartScan command execution"
STR_CSPSA_FQDN = "CspSubarrayFQDN :-> "
STR_GOTOIDLE_SUCCESS = "GoToIdle command is invoked successfully on CspSubarray."
STR_GOTOIDLE_EXEC = "GoToIdle command execution"

#INTEGERS
INT_SKA_LEVEL = 3