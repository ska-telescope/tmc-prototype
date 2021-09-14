"""
const file for CspSubarrayLeafNode
"""
# In/Out command constants
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_ALL_RESOURCES = "ReleaseAllResources"
CMD_ENDSCAN = "EndScan"
CMD_CONFIGURE = "Configure"
CMD_STARTSCAN = "Scan"
CMD_GOTOIDLE = "GoToIdle"
CMD_ABORT = "Abort"
CMD_RESET = "Reset"
CMD_RESTART = "Restart"
CMD_OBSRESET = "ObsReset"
CMD_TELESCOPE_ON = "TelescopeOn"
CMD_TELESCOPE_OFF = "TelescopeOff"

# Event messages
EVT_SUBSR_SA_RECEPTOR_ID_LIST = "receptorIDList"

# Error messages
ERR_IN_CREATE_PROXY = "Error in creating proxy of the Leaf Node device: "
ERR_INVALID_JSON = "Invalid JSON format while invoking command on CSP Subarray."
ERR_JSON_KEY_NOT_FOUND = "JSON key not found."
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the CSP Subarray \n"
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_EXCEPT_CONFIGURE_CMD_CB = "Exception in Configure CommandCallback: \n"
ERR_EXCEPT_STARTSCAN_CMD_CB = "Exception in StartScan CommandCallback: \n"
ERR_EXCEPT_ENDSCAN_CMD_CB = "Exception in EndScan CommandCallback: \n"
ERR_EXCEPT_RELEASE_ALL_RESOURCES_CMD_CB = (
    "Exception in ReleaseAllResources CommandCallback: \n"
)
ERR_EXCEPT_GO_TO_IDLE_CMD_CB = "Exception in GoToIdle CommandCallback: \n"
ERR_EXCEPT_ABORT_CMD_CB = "Exception in Abort CommandCallback: \n"
ERR_EXCEPT_RESTART_CMD_CB = "Exception in Restart CommandCallback: \n"
ERR_INIT_PROP_ATTR_CSPSALN = (
    "Error on initialising properties and attributes "
    "on CSP Subarray Leaf Node device."
)
ERR_MSG = "Error message is: "
ERR_RELEASE_ALL_RESOURCES = (
    "Error while invoking ReleaseAllResources command on CSP Subarray."
)
ERR_CONFIGURE_INVOKING_CMD = "Error while invoking Configure command on CSP Subarray."
ERR_ENDSCAN_INVOKING_CMD = "Error while invoking EndScan command on CSP Subarray."
ERR_INVALID_JSON_CONFIG = (
    "Invalid JSON format while invoking Configure command on CSP Subarray."
)
ERR_INVALID_JSON_ASSIGN_RES = (
    "Invalid JSON format while invoking AddReceptors command on CSP Subarray."
)
ERR_STARTSCAN_RESOURCES = "Error while invoking StartScan command on CSP Subarray."
ERR_DEVICE_NOT_READY = "CSP subarray is not in READY obsState."
ERR_DEVICE_NOT_READY_OR_IDLE = "CSP subarray is not in READY or IDLE obsState."
ERR_DEVICE_NOT_FAULT_ABORT = "CSP subarray is not in FAULT, ABORTED obsState."
ERR_DEVICE_NOT_IN_SCAN = "CSP Subarray is not in SCANNING obsState."
ERR_DEVICE_NOT_EMPTY_OR_IDLE = "CSP Subarray is not in EMPTY/IDLE obsState."
ERR_GOTOIDLE_INVOKING_CMD = "Error while invoking GoToIdle command on CSP Subarray."
ERR_ABORT_INVOKING_CMD = "Error while invoking Abort command on CSP Subarray."
ERR_RESET_INVOKING_CMD = "Error while invoking Reset command on CSP Subarray."
ERR_RESTART_INVOKING_CMD = "Error while invoking Restart command on CSP Subarray."
ERR_OBSRESET_INVOKING_CMD = "Error while invoking ObsReset command on CSP Subarray."
ERR_TELESCOPE_ON_INVOKING_CMD = "Error while invoking Telescope On command."
ERR_TELESCOPE_OFF_INVOKING_CMD = "Error while invoking Telescope Off command."
ERR_IN_CREATE_PROXY_CSPSA = "Error in creating proxy of the CSP Subarray device."
ERR_DEVFAILED_MSG = "This is error message for devfailed"
ERR_CALLBACK_CMD_FAILED = "CSP Subarray Leaf Node_Commandfailed in callback"
ERR_UNABLE_RESTART_CMD = "Unable to invoke Restart command"
ERR_UNABLE_ABORT_CMD = "Unable to invoke Abort command"
ERR_UNABLE_RESET_CMD = "Unable to invoke Reset command"
ERR_UNABLE_OBSRESET_CMD = "Unable to invoke ObsReset command"
ERR_RAISED_EXCEPTION = "CSP subarray leaf node raised exception"
ERR_DEVICE_NOT_IDLE = "CSP Subarray is not in IDLE obsState."
# strings
# General strings
STR_RECEPTOR_IDS = "receptor_ids"
STR_DISH = "dish"
STR_ERR_MSG = "Error message is: "
STR_ASSIGN_RESOURCES_SUCCESS = "Resources are assigned successfully on CSP Subarray."
STR_RELEASE_ALL_RESOURCES_SUCCESS = (
    "All the resources are removed from CSP Subarray successfully."
)
STR_CONFIGURE_SUCCESS = (
    "Configure command invoked successfully on CSP Subarray from "
    "CSP Subarray Leaf Node."
)
STR_ENDSCAN_SUCCESS = (
    "EndScan command invoked successfully on CspSubarray from CSP Subarray Leaf Node."
)
STR_CSPSALN_INIT_SUCCESS = "CSP Subarray Leaf Node initialized successfully."
STR_CMD_FAILED = "CSP Subarray Leaf Node_CommandFailed"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_CONFIG_EXEC = "Configure command execution"
STR_ENDSCAN_EXEC = "EndScan command execution"
STR_INVOKE_SUCCESS = " invoked successfully."
STR_COMMAND = "Command :-> "
STR_CMD_CALLBK = "CSP Subarray Leaf Node Command Callback"
STR_CONFIGURE_CMD_CALLBK = "CSP Subarray Leaf Node Configure Command Callback"
STR_STARTSCAN_CMD_CALLBK = "CSP Subarray Leaf Node StartScan Command Callback"
STR_ENDSCAN_CMD_CALLBK = "CSP Subarray Leaf Node EndScan Command Callback"
STR_RELEASE_RES_CMD_CALLBACK = (
    "CSP Subarray Leaf Node ReleaseAllResources Command Callback"
)
STR_GO_TO_IDLE_CMD_CALLBK = "CSP Subarray Leaf Node GoToIdle Command Callback"
STR_ABORT_CMD_CALLBK = "CSP Subarray Leaf Node Abort Command Callback"
STR_RESTART_CMD_CALLBK = "CSP Subarray Leaf Node Restart Command Callback"
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "


STR_FALSE = "False"
STR_STARTSCAN_SUCCESS = "Scan command is executed successfully."
PROP_DEF_VAL_CSP_MID_SA1 = "mid_csp/elt/subarray_01"
STR_START_SCAN_EXEC = "StartScan command execution"
STR_CSPSA_FQDN = "CspSubarrayFQDN :-> "
STR_GOTOIDLE_SUCCESS = "GoToIdle command is invoked successfully on CSP Subarray."
STR_ABORT_SUCCESS = "Abort command is invoked successfully on CSP Subarray."
STR_RESET_SUCCESS = "Reset command is invoked successfully on CSP Subarray."
STR_RESTART_SUCCESS = "Restart command is invoked successfully on CSP Subarray."
STR_OBSRESET_SUCCESS = "ObsReset command is invoked successfully on CSP Subarray."
STR_GOTOIDLE_EXEC = "GoToIdle command execution"
STR_ABORT_EXEC = "Abort command execution"
STR_RESET_EXEC = "Reset command execution"
STR_OBS_STATE = "CSP Subarray Leaf Node obsState is: "
STR_ON_CMD_ISSUED = "ON command invoked successfully from CSP Subarray Leaf Node."
STR_OFF_CMD_ISSUED = "OFF command invoked successfully from CSP Subarray Leaf Node."

# INTEGERS
INT_SKA_LEVEL = 3
