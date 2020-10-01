
"""
This file is part of the SubarrayNode project and defines variables used
"""

# ENUMS
from enum import IntEnum, unique


@unique
class PointingState(IntEnum):
    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3
    RESERVED = 4


# Events
EVT_MCCSSA_OBS_STATE = "mccsSubarrayObsState"
EVT_UNKNOWN = "Event from the Unknown device!"

# Commands
CMD_SCAN = "Scan"
CMD_START_SCAN= "StartScan"
CMD_CONFIGURE = "Configure"
CMD_END_SCAN = "EndScan"
CMD_ON = "On"
CMD_OFF = "Off"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_ALL_RESOURCES = "ReleaseAllResources"
CMD_END = "End"

# GROUPS
GRP_DISH_LEAF_NODE = "DishLeafNode_Group"

# strings
STR_MCCS_SA_LEAF_INIT_SUCCESS = "Subscribed MCCS Subarray attributes successfully."
STR_SA_INIT_SUCCESS = "Subarray node is initialized successfully."
STR_MCCS_SUBARRAY_OBS_STATE= "MCCS Subarray obsState is:"
STR_SA_INIT = "Initializing SubarrayNode..."
STR_CONFIGURE_CMD_INVOKED_SA_LOW = "Configure command invoked on Subarray Low"
STR_TRACK_CMD_INVOKED_SA = "Track command invoked on Subarray"
SCAN_ALREADY_IN_PROGRESS = "Scan is already in progress"
SCAN_ALREADY_COMPLETED = "Scan is already completed"
STR_SCAN_COMPLETE = "Scan is completed"
SCAN_NOT_EXECUTED = "Scan can not be executed as Subarray.obsState is not READY."
RESOURCE_ALREADY_RELEASED = "Resources are already released from Subarray"
STR_MCCS_END_SCAN_INIT = "MCCS EndScan is initiated."
STR_FALSE = "False"
STR_TRACK_EXEC = "Track command execution"
STR_CMD_FAILED = "SubarrayNodeLow_Commandfailed"
STR_CONFIGURE_EXEC = "Configure command execution"
STR_RELEASE_ALL_RES_EXEC = "ReleaseAllResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_END_SCAN_EXEC = "ENDSCAN command execution"
STR_SCAN_EXEC = "SCAN command execution"
STR_MCCS_SCAN_INIT = "MCCS Subarray Leaf Node Scan is initiated."
STR_SCAN_SUCCESS = "Scan command is executed successfully."
STR_END_SCAN_SUCCESS = "EndScan command is executed successfully."
STR_END_SUCCESS = "End command invoked successfully on Mccs Subarray Leaf Node."
STR_END_EXEC = "End command execution."
STR_CMD_END_INV_MCCS = "End command is invoked on MccsSubarrayLeafNode."

# Error messages
ERR_SUBS_MCCS_SA_LEAF_ATTR = "Exception occurred while subscribing to MCCS Subarray attribute"
ERR_SUBSR_MCCSSA_OBS_STATE = "Error in subscribing MCCS Subarray obsState on MCCSSALN LeafNodes."
ERR_MCCS_SUBARRAY_OBS_STATE = "Key Error occurred while setting MCCS Subarray obsState"
ERR_INVOKING_ON_CMD = "Error while invoking ON command on Subarray Node."
ERR_INVOKING_OFF_CMD = "Error while invoking OFF command on Subarray Node."
ERR_END_INVOKING_CMD = "Error while invoking End command on Subarray Node low."
ERR_END_SCAN_CMD_ON_MCCS="Error invoking EndScan command on MccsSubarrayLeafNode"
ERR_DEVICE_NOT_READY = "Subarray Node low is not in Ready observation state."


# JSON keys
PROP_DEF_VAL_TMMCCS_MID_SALN = "ska_low/tm_leaf_node/mccs_subarray01"
