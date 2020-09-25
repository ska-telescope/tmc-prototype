"""
const file for MCCSSubarrayLeafNode
"""
# In/Out command constants
CMD_END = "End"
CMD_STARTSCAN = "Scan"

#Event messages

#Error messages
ERR_IN_CREATE_PROXY_MCCSSA = "Error in creating proxy of the MCCS Subarray device."
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_END_INVOKING_CMD = "Error while invoking End command on MCCS Subarray."
ERR_DEVICE_NOT_READY = "MCCS subarray is not in READY obsState."
ERR_STARTSCAN_RESOURCES = "Error while invoking StartScan command on MCCS Subarray."

#strings
#General strings
STR_MCCSSALN_INIT_SUCCESS = "MCCSSubarrayLeafNode initialized successfully."
STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = " invoked successfully."
STR_END_SUCCESS = "End command is invoked successfully on MccsSubarray."
STR_OBS_STATE = "MCCS Subarray Leaf Node obsState is: "
STR_STARTSCAN_SUCCESS = "Scan command is executed successfully."
STR_START_SCAN_EXEC = "StartScan command execution"



#INTEGERS
INT_SKA_LEVEL = 3
