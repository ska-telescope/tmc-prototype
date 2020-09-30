
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
CMD_ENDSB = "End"

# GROUPS
GRP_DISH_LEAF_NODE = "DishLeafNode_Group"

# strings
STR_MCCS_SA_LEAF_INIT_SUCCESS = "Subscribed MCCS Subarray attributes successfully."
STR_SA_INIT_SUCCESS = "Subarray node is initialized successfully."
STR_MCCS_SUBARRAY_OBS_STATE= "MCCS Subarray obsState is:"
STR_SA_INIT = "Initializing SubarrayNode..."



# Error messages
ERR_SUBS_MCCS_SA_LEAF_ATTR = "Exception occurred while subscribing to MCCS Subarray attribute"
ERR_SUBSR_MCCSSA_OBS_STATE = "Error in subscribing MCCS Subarray obsState on MCCSSALN LeafNodes."
ERR_MCCS_SUBARRAY_OBS_STATE = "Key Error occurred while setting MCCS Subarray obsState"
ERR_INVOKING_ON_CMD = "Error while invoking ON command on Subarray Node."
ERR_INVOKING_OFF_CMD = "Error while invoking OFF command on Subarray Node."



# JSON keys
PROP_DEF_VAL_TMMCCS_MID_SALN = "ska_low/tm_leaf_node/mccs_subarray01"
