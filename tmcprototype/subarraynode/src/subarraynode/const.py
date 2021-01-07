
"""
This file is part of the SubarrayNode project and defines variables used
"""

# ENUMS
from enum import IntEnum, unique


@unique
class PointingState(IntEnum):
    NONE = 0
    READY = 1
    SLEW = 2
    TRACK = 3
    SCAN = 4
    UNKNOWN = 5

# Events
EVT_DISH_HEALTH_STATE = "dishHealthState"
EVT_DISH_POINTING_STATE = "dishPointingState"
EVT_CSPSA_HEALTH = "cspsubarrayHealthState"
EVT_SDPSA_HEALTH = "sdpSubarrayHealthState"
EVT_CSPSA_OBS_STATE = "cspSubarrayObsState"
EVT_SDPSA_OBS_STATE = "sdpSubarrayObsState"
EVT_UNKNOWN = "Event from the Unknown device!"

# Commands
CMD_SCAN = "Scan"
CMD_START_SCAN= "StartScan"
CMD_CONFIGURE = "Configure"
CMD_END_SCAN = "EndScan"
CMD_TRACK = "Track"
CMD_STOP_TRACK = "StopTrack"
CMD_ON = "On"
CMD_OFF = "Off"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_ALL_RESOURCES = "ReleaseAllResources"
CMD_END = "End"
CMD_GOTOIDLE = "GoToIdle"
CMD_RESTART = "Restart"
CMD_ABORT = "Abort"
CMD_OBSRESET = "ObsReset"

# GROUPS
GRP_DISH_LEAF_NODE = "DishLeafNode_Group"

# strings
STR_CMD_STOP_TRACK_INV_DLN = "StopTrack command is invoked on DishLeafNodesGroup"
STR_CMD_END_INV_SDP = "End command is invoked on SdpSubarrayLeafNode."
STR_CMD_GOTOIDLE_INV_CSP = "GoToIdle command is invoked on CspSubarrayLeafNode."
STR_CMD_RESTART_INV_SDP = "Command Restart is invoked on SDP Subarray Leaf Node."
STR_CMD_RESTART_INV_CSP = "Command Restart is invoked on CSP Subarray Leaf Node."
STR_CMD_RESTART_INV_DISH_GROUP = "Command Restart is invoked on group of Dishes."
STR_CMD_OBSRESET_INV_SDP = "Command ObsReset is invoked on SDP Subarray Leaf Node."
STR_CMD_OBSRESET_INV_CSP = "Command ObsReset is invoked on CSP Subarray Leaf Node."
STR_CMD_OBSRESET_INV_DISH_GROUP = "Command ObsReset is invoked on group of Dishes."
STR_CMD_ABORT_INV_SDP = "Command Abort is invoked on SDP Subarray Leaf Node."
STR_CMD_ABORT_INV_CSP = "Command Abort is invoked on CSP Subarray Leaf Node."
STR_ASSIGN_RESOURCES_INV_CSP_SALN = "Assign Resources is invoked on CSPSubarrayLeafNode"
STR_ASSIGN_RESOURCES_INV_SDP_SALN = "Assign Resources is invoked on SDPSubarrayLeafNode"
STR_RELEASE_ALL_RESOURCES_CSP_SALN = "ReleaseAllResources command is invoked on CSPSubarrayLeafNode"
STR_RELEASE_ALL_RESOURCES_SDP_SALN = "ReleaseAllResources command is invoked on SDPSubarrayLeafNode"
STR_SCAN_IP_ARG = "Scan inputs Arguments :-> "
STR_GRP_DEF_SCAN_FN = "Group Definitions in scan function :-> "
STR_SA_SCANNING = "Subarray is scanning at the desired pointing coordinates."
STR_CMD_ABORT_INV_DLN = "Command Abort is invoked on Dish Leaf Nodes Group"
STR_GRP_DEF_END_SCAN_FN = "Group Definitions in EndScan function :-> "
STR_SCAN_COMPLETE = "Scan is completed"
STR_DISH_LN_VS_HEALTH_EVT_ID = "self._dishLnVsHealthEventID "
STR_DISH_LN_VS_POINTING_STATE_EVT_ID = "self._dishLnVsPointingStateEventID "
STR_CSP_LN_HEALTH_EVT_ID = "CSP Subarray Leaf Node Health State subscribed"
STR_CSP_LN_OBS_STATE_EVT_ID = "CSP Subarray Leaf Node ObsState subscribed"
STR_SDP_LN_HEALTH_EVT_ID = "SDP Subarray Leaf Node Health State subscribed"
STR_SDP_LN_OBS_STATE_EVT_ID = "SDP Subarray Leaf Node ObsState subscribed"
STR_GRP_DEF = "Receptors in the Group :-> "
STR_LN_PROXIES = "LeafNode proxies :-> "
STR_SUBS_ATTRS_LN = "Subscribing attributes of Leaf Nodes..."
STR_HS_EVNT_ID = "DishHealth EventID array is:"
RECEPTORS_REMOVE_SUCCESS = "Receptors are removed successfully"
STR_ASSIGN_RES_SUCCESS = "Receptors are assigned successfully."
STR_DISH_PROXY_LIST = "Dishproxy list"
STR_HEALTH_ID = "health id "
STR_POINTING_STATE_ID = "pointing state id "
STR_RECEPTORS_REMOVE_SUCCESS = "All the receptors are removed from the Subarray node."
STR_HEALTH_STATE = "healthState of "
STR_POINTING_STATE = "pointingState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = "Subarray healthState event returned unknown value  \n"
STR_READY = " :-> READY"
STR_SLEW = " :-> SLEW"
STR_TRACK = " :-> TRACK"
STR_SCAN = " :-> SCAN"
STR_POINTING_STATE_UNKNOWN_VAL = "Subarray pointingState event returned unknown value  \n"
STR_ARROW = " :-> "
STR_SA_INIT = "Initializing SubarrayNode..."
STR_SA_INIT_SUCCESS = "Subarray node is initialized successfully."
STR_SA_PROXY_INIT = "Creating proxy for -> "

STR_CONFIGURE_IP_ARG = "Input Arguments for Configure command :-> "
STR_GRP_DEF_CONFIGURE_FN = "Group devices during Configure command :-> "
STR_TRACK_IP_ARG = "Input Arguments for Track command :-> "
STR_GRP_DEF_TRACK_FN = "Group devices during Track command :-> "

STR_CONFIGURE_CMD_INVOKED_SA = "Configure command invoked on Subarray"
STR_TRACK_CMD_INVOKED_SA = "Track command invoked on Subarray"
SCAN_ALREADY_IN_PROGRESS = "Scan is already in progress"
SCAN_ALREADY_COMPLETED = "Scan is already completed"
SCAN_NOT_EXECUTED = "Scan can not be executed as Subarray.obsState is not READY."
RESOURCE_ALREADY_RELEASED = "Resources are already released from Subarray"
STR_FALSE = "False"
STR_TRACK_EXEC = "Track command execution"
STR_CMD_FAILED = "SubarrayNode_Commandfailed"
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
STR_SDP_SCAN_INIT = "SDP Scan is initiated."
STR_CSP_SCAN_INIT = "CSP Scan is initiated."
STR_SDP_END_SCAN_INIT = "SDP EndScan is initiated."
STR_CSP_END_SCAN_INIT = "CSP EndScan is initiated."
STR_CSP_SA_LEAF_SUB_SUCCESS = "Subscribed Csp Subarray attributes successfully."
STR_SDP_SA_LEAF_SUB_SUCCESS = "Subscribed Sdp Subarray attributes successfully."
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
ERR_SCAN_CMD = "Exception in Scan command: "
ERR_END_SCAN_CMD = "Exception in End Scan command:"
ERR_ASSIGN_RES_CMD = "Exception in AssignResources command: "
ERR_RELEASE_RES_CMD = "Exception occurred in ReleaseAllResources command."
ERR_AGGR_HEALTH_STATE = "Error while aggregating healthState \n"
ERR_AGGR_POINTING_STATE = "Error while aggregating pointingState \n"
ERR_AGGR_OBS_STATE = "Error while aggregating obsState \n"
ERR_AGGR_DEVICE_STATE = "Error while aggregating deviceState \n"
ERR_SUBSR_SA_HEALTH_STATE = "Error in subscribing Subarray healthState \n"
ERR_SUBSR_DSH_POINTING_STATE = "Error in subscribing Dish pointingState \n"
ERR_CONFIGURE_CMD = "Exception in Configure command: \n "
ERR_ADDING_LEAFNODE = "Exception occurred while adding LeafNodes "
ERR_END_SCAN_CMD_ON_GROUP = "Error invoking EndScan command on DishLeafNode group"
ERR_RELEASE_RES_CMD_GROUP = "Error invoking AssignResources command on DishLeafNode group"
ERR_SETHEALTH_CALLBK = "KeyError occurred in setHealth callback of SubarrayNode "
ERR_SETPOINTING_CALLBK = "KeyError occurred in setPointing callback of SubarrayNode "
ERR_CONFIGURE_CMD_GROUP = "Error invoking Configure command on DishLeafNode group "
ERR_INVALID_DATATYPE = " Invalid argument "
ERR_DUPLICATE_END_SCAN_CMD = "End Scan Command Already Executed"
ERR_DUPLICATE_SCAN_CMD = "Scan Command Already Executed"
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_TRACK_CMD = "Exception in Track command: \n "
ERR_CSP_CMD = "Failed to send command to CSP Subarray Leaf Node."
ERR_SDP_CMD = "Failed to send command to SDP Subarray Leaf Node."
ERR_CREATE_PROXY= "Failed to create proxy on SubarrayNode."
ERR_INVOKE_ON_CMD_ON_SA = "Failed to invoke On command on SubarrayNode."
ERR_ON_SUBS_CSP_SA_HEALTH = "Error in subscribing cspsubarrayHealthState attribute."
ERR_CSP_SA_HEALTH_CB = "Error in cspsubarrayHealthCallback."
ERR_SUBS_CSP_SA_LEAF_ATTR = "Exception occurred while subscribing to Csp Subarray attribute"
ERR_CSP_SA_LEAF_INIT = "Error occured in Csp Subarray Leaf Node initialization "
ERR_CSPSDP_SUBARRAY_HEALTHSTATE = "Key Error occurred while setting CSP/SDP Subarray healthState"
ERR_SUBSR_CSPSDPSA_HEALTH_STATE = "Error in subscribing CSP/SDP Subarray healthState on respective " \
                                  "LeafNodes. \n"
ERR_DEVICE_NOT_READY = "Subarray Node is not in Ready observation state."
ERR_ENDSB_INVOKING_CMD = "Error while invoking EndSB command on Subarray Node."
ERR_INVOKING_ON_CMD = "Error while invoking ON command on Subarray Node."
ERR_INVOKING_OFF_CMD = "Error while invoking OFF command on Subarray Node."
ERR_RESTART_INVOKING_CMD = "Error while invoking Restart command on Subarray Node."
ERR_OBSRESET_INVOKING_CMD = "Error while invoking ObsReset command on Subarray Node."
ERR_ABORT_INVOKING_CMD = "Error while invoking ABORT command on Subarray Node."
ERR_CSPSDP_SUBARRAY_OBS_STATE = "Key Error occurred while setting CSP/SDP Subarray obsState"
ERR_SUBSR_CSPSDPSA_OBS_STATE = "Error in subscribing CSP/SDP Subarray obsState on respective " \
                                  "LeafNodes. \n"
ERR_SUBSR_CSPSDPSA_DEVICE_STATE = "Error in subscribing CSP/SDP Subarray Device state"
ERR_SUBS_SDP_SA_LEAF_ATTR = "Exception occurred while subscribing to SDP Subarray attribute"
ERR_SDP_SA_LEAF_INIT = "Error occured in SDP Subarray Leaf Node initialization "
ERR_SUBSR_RECEIVE_ADDRESSES_SDP_SA = "Error in subscribing receive addresses of SDP Subarray"
ERR_SA_INIT = "Subarray node initialization failed."
ERR_CSP_PROXY_CREATE = "CSP Proxy creaton failed on Subarray Node"
ERR_SDP_PROXY_CREATE = "SDP Proxy creaton failed on Subarray Node"

# JSON keys
STR_KEY_DISH = "dish"
STR_KEY_RECEPTOR_ID_LIST = "receptorIDList"
STR_KEY_PB_ID_LIST = "processingBlockIdList"

PROP_DEF_VAL_TMCSP_MID_SALN = "ska_mid/tm_leaf_node/csp_subarray"
PROP_DEF_VAL_TMSDP_MID_SALN = "ska_mid/tm_leaf_node/sdp_subarray"
PROP_DEF_VAL_LEAF_NODE_PREFIX = "ska_mid/tm_leaf_node/d"
