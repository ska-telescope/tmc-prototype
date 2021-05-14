"""
This file is part of the SubarrayNode project and defines variables used
"""
# Events
EVT_MCCSSA_OBS_STATE = "mccsSubarrayObsState"
EVT_MCCSSA_HEALTH = "mccsSubarrayHealthState"
EVT_MCCSSA_ASSIGNED_RESOURCES = "mccs_assigned_resources"
EVT_UNKNOWN = "Event from the Unknown device!"

# Commands
CMD_SCAN = "Scan"
CMD_CONFIGURE = "Configure"
CMD_END_SCAN = "EndScan"
CMD_ON = "On"
CMD_OFF = "Off"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_ALL_RESOURCES = "ReleaseAllResources"
CMD_END = "End"
CMD_OBSRESET = "ObsReset"
CMD_ABORT = "Abort"
CMD_RESTART = "Restart"


# strings
STR_SUB_ATTR_MCCS_SALN_HEALTH_SUCCESS = (
    "Subscribed MCCS Subarray Health State attributes successfully."
)
STR_SUB_ATTR_MCCS_SALN_OBSTATE_SUCCESS = (
    "Subscribed MCCS Subarray ObsState attributes successfully."
)
STR_SUB_ATTR_MCCS_SALN_ASSIGNED_RESOURCES_SUCCESS = (
    "Subscribed MCCS Subarray assigned_resources attribute successfully"
)
STR_SA_INIT_SUCCESS = "Subarray node is initialized successfully."
STR_SA_INIT = "Initializing SubarrayNode..."
STR_CONFIGURE_IP_ARG = "Input Arguments for Configure command :-> "
STR_GRP_DEF_CONFIGURE_FN = "Group devices during Configure command :-> "
STR_TRACK_IP_ARG = "Input Arguments for Track command :-> "
STR_GRP_DEF_TRACK_FN = "Group devices during Track command :-> "
STR_CONFIGURE_CMD_INVOKED_SA_LOW = "Configure command invoked on SubarrayNode Low."
STR_END_CMD_INVOKED_SA_LOW = "End command invoked on SubarrayNodelow."
STR_TRACK_CMD_INVOKED_SA = "Track command invoked on Subarray"
SCAN_ALREADY_IN_PROGRESS = "Scan is already in progress"
SCAN_ALREADY_COMPLETED = "Scan is already completed"
STR_SCAN_COMPLETE = "Scan is completed"
SCAN_NOT_EXECUTED = "Scan can not be executed as Subarray.obsState is not READY."
RESOURCE_ALREADY_RELEASED = "Resources are already released from Subarray"
STR_MCCS_END_SCAN_INIT = "MCCS EndScan is initiated."
STR_CMD_ABORT_INV_MCCS = "Abort command invoked successfully on MccsSubarrayLeafNode."
STR_CMD_RESTART_INV_CSP = "Restart command is invoked on MccsSubarrayLeafNode."
STR_ABORT_SUCCESS = "Abort command invoked successfully."
STR_FALSE = "False"
STR_TRACK_EXEC = "Track command execution"
STR_CMD_FAILED = "SubarrayNodeLow_Commandfailed"
STR_CONFIGURE_EXEC = "Configure command execution"
STR_RELEASE_ALL_RES_EXEC = "ReleaseAllResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_END_SCAN_EXEC = "ENDSCAN command execution"
STR_RELEASE_EXEC = "RELEASE RESOURCES command execution"
STR_SCAN_EXEC = "SCAN command execution"
STR_MCCS_SCAN_INIT = "MCCS Subarray Leaf Node Scan is initiated."
STR_SCAN_SUCCESS = "Scan command is executed successfully."
STR_END_SCAN_SUCCESS = "EndScan command is executed successfully."
STR_END_SUCCESS = "End command invoked successfully on MCCS Subarray Leaf Node."
STR_END_EXEC = "End command execution."
STR_CMD_END_INV_MCCS = "End command is invoked on MccsSubarrayLeafNode."
STR_RELEASE_SUCCESS = "RELEASEALLRESOURCES command invoked successfully."
STR_HEALTH_STATE = "healthState of "
STR_ARROW = " :-> "
STR_HEALTH_STATE_UNKNOWN_VAL = "Subarray healthState event returned unknown value  \n"
STR_MCCS_SUBARRAY_OBS_STATE = "MCCS Subarray obsState is:"
STR_SCAN_IP_ARG = "Scan inputs Arguments :-> "
STR_SA_SCANNING = "Subarray is scanning at the desired pointing coordinates."
STR_OBSRESET_SUCCESS = "ObsReset command is invoked on MccsSubarrayLeafNode."
ERR_OBSRESET_INVOKING_CMD = (
    "Error while invoking ObsReset command on Subarray Node Low."
)
STR_OBSRESET_EXEC = "ObsReset command execution."
STR_RESTART_EXEC = "Restart command execution."
STR_CMD_OBSRESET_INV_MCCSSLN = "Command ObsReset is invoked on MccsSubarrayLeafNode."
STR_RESTART_SUCCESS = "Restart command invoked successfully on MccsSubarrayLeafNode."

# Error messages
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found"
ERR_SCAN_CMD = "Exception in Scan command: "
ERR_SUBS_MCCS_SA_LEAF_ATTR = (
    "Exception occurred while subscribing to MCCS Subarray attribute"
)
ERR_SUBSR_MCCSSA_OBS_STATE = (
    "Error in subscribing MCCS Subarray obsState on MCCSSALN LeafNodes."
)
ERR_MCCS_SUBARRAY_OBS_STATE = "Key Error occurred while setting MCCS Subarray obsState"
ERR_INVOKING_ON_CMD = "Error while invoking ON command on Subarray Node."
ERR_INVOKING_OFF_CMD = "Error while invoking OFF command on Subarray Node."
ERR_END_INVOKING_CMD = "Error while invoking End command on Subarray Node low."
ERR_RESTART_INVOKING_CMD = "Error while invoking Restart command on Subarray Node."
ERR_END_SCAN_CMD_ON_MCCS = "Error invoking EndScan command on MccsSubarrayLeafNode"
ERR_DEVICE_NOT_READY = "Subarray Node low is not in Ready observation state."
ERR_MCCS_CMD = "Failed to send command to MCCS Subarray Leaf Node."
ERR_SUBSR_SA_HEALTH_STATE = "Error in subscribing Subarray healthState \n"
ERR_SUBSR_MCCSSA_ASSIGNED_RES_ATTR = "Error in subscribing assigned_resources attribute "
ERR_ABORT_INVOKING_CMD = "Error while invoking Abort command."


# JSON keys
PROP_DEF_VAL_TMMCCS_MID_SALN = "ska_low/tm_leaf_node/mccs_subarray01"
