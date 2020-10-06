"""
const file for MccsSubarrayLeafNode
"""
# In/Out command constants
CMD_CONFIGURE = "Configure"
CMD_END = "End"
CMD_SCAN = "Scan"
CMD_ENDSCAN = "EndScan"

#Event messages

#Error messages
ERR_IN_CREATE_PROXY_MCCSSA = "Error in creating proxy of the MCCS Subarray device."
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_JSON_KEY_NOT_FOUND = "JSON key not found."
ERR_CONFIGURE_INVOKING_CMD = "Error while invoking Configure command on MCCS Subarray."
ERR_DEVFAILED_MSG = "This is error message for devfailed"
ERR_CALLBACK_CMD_FAILED = "MccsSubarrayLeafNode_Commandfailed in callback"
ERR_INVALID_JSON_CONFIG = "Invalid JSON format while invoking Configure command on MccsSubarray."

ERR_END_INVOKING_CMD = "Error while invoking End command on MCCS Subarray."
ERR_DEVICE_NOT_READY = "MCCS subarray is not in READY obsState."
ERR_SCAN_RESOURCES = "Error while invoking Scan command on MCCS Subarray."
ERR_DEVICE_NOT_SCANNING = "MCCS subarray is not in SCANNING obsState."
ERR_ENDSCAN_COMMAND = "Error while invoking EndScan command on MCCS Subarray."
STR_END_EXEC = "End command execution"

#strings
#General strings
STR_MCCSSALN_INIT_SUCCESS = "MCCSSubarrayLeafNode initialized successfully."
STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = " invoked successfully."
STR_CONFIGURE_SUCCESS = "Configure command invoked successfully on MccsSubarray from " \
                            "MccsSubarrayLeafNode."
STR_CONFIGURE_EXEC = "Configure command execution"
STR_CMD_FAILED = "MccsSubarrayLeafNode_CommandFailed"
STR_END_SUCCESS = "End command is invoked successfully on MccsSubarray."
STR_OBS_STATE = "MCCS Subarray Leaf Node obsState is: "
STR_SCAN_SUCCESS = "Scan command is executed successfully."
STR_SCAN_EXEC = "Scan command execution"
STR_ENDSCAN_SUCCESS = "EndScan command is executed successfully."
STR_END_SCAN_EXEC = "EndScan command execution"
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "

#INTEGERS
INT_SKA_LEVEL = 3
