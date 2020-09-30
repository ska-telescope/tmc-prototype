
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
STR_CONFIGURE_CMD_INVOKED_SA_LOW = "Configure command invoked on Subarray Low"
STR_TRACK_CMD_INVOKED_SA = "Track command invoked on Subarray"
SCAN_ALREADY_IN_PROGRESS = "Scan is already in progress"
SCAN_ALREADY_COMPLETED = "Scan is already completed"
SCAN_NOT_EXECUTED = "Scan can not be executed as Subarray.obsState is not READY."
RESOURCE_ALREADY_RELEASED = "Resources are already released from Subarray"
STR_FALSE = "False"
STR_TRACK_EXEC = "Track command execution"
STR_CMD_FAILED = "SubarrayNodeLow_Commandfailed"
STR_CONFIGURE_EXEC = "Configure command execution"
STR_RELEASE_ALL_RES_EXEC = "ReleaseAllResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_END_SCAN_EXEC = "ENDSCAN command execution"
STR_SCAN_EXEC = "SCAN command execution"
STR_DISH_ALLOCATION = "Allocating dishes"
STR_CSP_ALLOCATION = "Allocating CSP resources"
STR_SDP_ALLOCATION = "Allocating SDP resources"
STR_DISH_ALLOCATION_RESULT = "Dish allocation result: "
STR_CSP_ALLOCATION_RESULT = "CSP allocation result: "
STR_SDP_ALLOCATION_RESULT = "SDP allocation result: "
STR_DISH_RELEASE = "Releasing dishes"
STR_CSP_RELEASE = "Releasing CSP resources"
STR_SDP_RELEASE = "Releasing SDP resources"
STR_CSP_SA_HEALTH_OK = "CSP SA health is OK."
STR_CSP_SA_HEALTH_DEGRADED = "CSP SA health is DEGRADED."
STR_CSP_SA_HEALTH_FAILED = "CSP SA health is FAILED."
STR_CSP_SA_HEALTH_UNKNOWN = "CSP SA health is UNKNOWN."
STR_CSP_SUBARRAY_OBS_STATE= "CSP Subarray obsState is:"
STR_SDP_SUBARRAY_OBS_STATE= "SDP Subarray obsState is:"
STR_MCCS_SCAN_INIT = "MCCS Subarray Leaf Node Scan is initiated."
STR_SDP_END_SCAN_INIT = "SDP EndScan is initiated."
STR_CSP_END_SCAN_INIT = "CSP EndScan is initiated."
STR_CSP_SA_LEAF_INIT_SUCCESS = "Subscribed Csp Subarray attributes successfully."
STR_SDP_SA_LEAF_INIT_SUCCESS = "Subscribed Sdp Subarray attributes successfully."
STR_SCAN_SUCCESS = "Scan command is executed successfully."
STR_END_SCAN_SUCCESS = "EndScan command is executed successfully."
STR_DELAY_MODEL_SUB_POINT = "delayModelSubscriptionPoint"
STR_VIS_DESTIN_ADDR_SUB_POINT = "visDestinationAddressSubscriptionPoint"
STR_CSP_CBFOUTLINK = "cspCbfOutlinkAddress"
STR_ENDSB_SUCCESS = "EndSB command invoked successfully on SDP Subarray Leaf Node and CSP Subarray Leaf Node."
STR_ABORT_SUCCESS = "Abort command invoked successfully on SDP Subarray Leaf Node and CSP Subarray Leaf Node and Dish Leaf Node."
STR_ENDSB_EXEC = "EndSB command execution."
STR_RESTART_EXEC = "Restart command execution."
STR_OBSRESET_EXEC = "ObsReset command execution."
STR_RESTART_SUCCESS = "Restart command invoked successfully on SDP Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node."
STR_OBSRESET_SUCCESS = "ObsReset command invoked successfully on SDP Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node."

# Error messages
ERR_SUBS_MCCS_SA_LEAF_ATTR = "Exception occurred while subscribing to MCCS Subarray attribute"
ERR_SUBSR_MCCSSA_OBS_STATE = "Error in subscribing MCCS Subarray obsState on MCCSSALN LeafNodes."
ERR_MCCS_SUBARRAY_OBS_STATE = "Key Error occurred while setting MCCS Subarray obsState"
ERR_INVOKING_ON_CMD = "Error while invoking ON command on Subarray Node."
ERR_INVOKING_OFF_CMD = "Error while invoking OFF command on Subarray Node."



# JSON keys
PROP_DEF_VAL_TMMCCS_MID_SALN = "ska_low/tm_leaf_node/mccs_subarray01"
