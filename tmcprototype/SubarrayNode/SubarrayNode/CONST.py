
"""
This file is part of the SubarrayNode project and defines variables used
"""

# ENUMS
from enum import IntEnum, unique

@unique
class HealthState(IntEnum):
    OK = 0
    DEGRADED = 1
    FAILED = 2
    UNKNOWN = 3


@unique
class PointingState(IntEnum):
    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3
    RESERVED = 4


@unique
class AdminMode(IntEnum):
    ONLINE = 0
    OFFLINE = 1
    MAINTENANCE = 2
    NOTIFIED = 3
    RESERVED = 4


@unique
class ObsState(IntEnum):
    IDLE = 0
    CONFIGURING = 1
    READY = 2
    SCANNING = 3
    PAUSED = 4
    ABORTED = 5
    FAULT = 6


@unique
class ObsMode(IntEnum):
    IDLE = 0
    IMAGING = 1
    PULSARSEARCH = 2
    PULSARTIMING = 3
    DYNAMICSPECTRUM = 4
    TRANSIENTSEARCH = 5
    VLBI = 6
    CALIBRATION = 7


#Events
EVT_DISH_HEALTH_STATE = "dishHealthState"
EVT_DISH_POINTING_STATE = "dishPointingState"
EVT_CSPSA_HEALTH = "cspsubarrayHealthState"
EVT_SDPSA_HEALTH = "sdpSubarrayHealthState"
EVT_CSPSA_OBS_STATE = "cspSubarrayObsState"
EVT_SDPSA_OBS_STATE = "sdpSubarrayObsState"
EVT_UNKNOWN = "Event from the Unknown device!"

#Commands
CMD_SCAN = "Scan"
CMD_START_SCAN= "StartScan"
CMD_CONFIGURE = "Configure"
CMD_END_SCAN = "EndScan"
CMD_TRACK = "Track"
CMD_STOP_TRACK = "StopTrack"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_ALL_RESOURCES = "ReleaseAllResources"
CMD_CONFIGURESCAN = "ConfigureScan"
CMD_ENDSB = "EndSB"


#GROUPS
GRP_DISH_LEAF_NODE = "DishLeafNode_Group"

#strings
STR_SCAN_IP_ARG = "Scan inputs Arguments :-> "
STR_GRP_DEF_SCAN_FN = "Group Definitions in scan function :-> "
STR_SA_SCANNING = "Subarray is scanning at the desired pointing coordinates."

STR_GRP_DEF_END_SCAN_FN = "Group Definitions in EndScan function :-> "
STR_SCAN_COMPLETE = "Scan is completed"
STR_DISH_LN_VS_HEALTH_EVT_ID = "self._dishLnVsHealthEventID "
STR_DISH_LN_VS_POINTING_STATE_EVT_ID = "self._dishLnVsPointingStateEventID "
STR_GRP_DEF = "Group definition :-> "
STR_LN_PROXIES = "LeafNode proxies :-> "
STR_SUBS_ATTRS_LN = "Subscribing attributes of Leaf Nodes..."
STR_HS_EVNT_ID = "DishHealth EventID array is:"

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

STR_CONFIGURE_IP_ARG = "Input Arguments for Configure command :-> "
STR_GRP_DEF_CONFIGURE_FN = "Group devices during Configure command :-> "
STR_TRACK_IP_ARG = "Input Arguments for Track command :-> "
STR_GRP_DEF_TRACK_FN = "Group devices during Track command :-> "

STR_CONFIGURE_CMD_INVOKED_SA = "Configure command invoked on Subarray"
STR_TRACK_CMD_INVOKED_SA = "Track command invoked on Subarray"
SCAN_ALREADY_IN_PROGRESS = "Scan is already in progress"
SCAN_ALREADY_COMPLETED = "Scan is already completed"
SCAN_NOT_EXECUTED = "Scan can not be executed as Subarray.obsState is not READY."
RESRC_ALREADY_RELEASED = "Resources are already released from Subarray"
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
STR_CSP_SA_HEALTH_OK = "CSP SA health is OK."
STR_CSP_SA_HEALTH_DEGRADED = "CSP SA health is DEGRADED."
STR_CSP_SA_HEALTH_FAILED = "CSP SA health is FAILED."
STR_CSP_SA_HEALTH_UNKNOWN = "CSP SA health is UNKNOWN."
STR_CSP_SA_LEAF_INIT_SUCCESS = "Csp Subarray Leaf Node initialized successfully."
STR_SDP_SA_LEAF_INIT_SUCCESS = "Sdp Subarray Leaf Node initialized successfully."
STR_SCAN_SUCCESS = "Scan command is executed successfully."
STR_END_SCAN_SUCCESS = "EndScan command is executed successfully."
STR_HEALTH_STATE = "healthState of "
STR_HEALTH_STATE_UNKNOWN_VAL = "healthState event returned unknown value \n"
STR_DELAY_MODEL_SUB_POINT = "delayModelSubscriptionPoint"
STR_VIS_DESTIN_ADDR_SUB_POINT = "visDestinationAddressSubscriptionPoint"
STR_CSP_CBFOUTLINK = "cspCbfOutlinkAddress"
STR_ENDSB_SUCCESS = "EndSB command invoked successfully on SDP Subarray Leaf Node and CSP Subarray Leaf Node."
STR_ENDSB_EXEC = "EndSB command execution."


#Error messages
ERR_SCAN_CMD = "Exception in Scan command: "
ERR_END_SCAN_CMD = "Exception in End Scan command:"
ERR_ASSIGN_RES_CMD = "Exception in AssignResources command: "
ERR_RELEASE_RES_CMD = "Exception occurred in ReleaseAllResources command."
ERR_AGGR_HEALTH_STATE = "Error while aggregating healthState \n"
ERR_AGGR_POINTING_STATE = "Error while aggregating pointingState \n"
ERR_AGGR_OBS_STATE = "Error while aggregating obsState \n"
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
ERR_ON_SUBS_CSP_SA_HEALTH = "Error in subscribing cspsubarrayHealthState attribute."
ERR_CSP_SA_HEALTH_CB = "Error in cspsubarrayHealthCallback."
ERR_SUBS_CSP_SA_LEAF_ATTR = "Exception occurred while subscribing to Csp Subarray attribute"
ERR_CSP_SA_LEAF_INIT = "Error occured in Csp Subarray Leaf Node initialization "
ERR_CSPSDP_SUBARRAY_HEALTHSTATE = "Key Error occurred while setting CSP/SDP Subarray healthState"
ERR_SUBSR_CSPSDPSA_HEALTH_STATE = "Error in subscribing CSP/SDP Subarray healthState on respective " \
                                  "LeafNodes. \n"
ERR_DEVICE_NOT_READY = "Subarray Node is not in Ready observation state."
ERR_ENDSB_INVOKING_CMD = "Error while invoking EndSB command on Subarray Node."


ERR_CSPSDP_SUBARRAY_OBS_STATE = "Key Error occurred while setting CSP/SDP Subarray obsState"
ERR_SUBSR_CSPSDPSA_OBS_STATE = "Error in subscribing CSP/SDP Subarray obsState on respective " \
                                  "LeafNodes. \n"

ERR_SUBS_SDP_SA_LEAF_ATTR = "Exception occurred while subscribing to SDP Subarray attribute"
ERR_SDP_SA_LEAF_INIT = "Error occured in SDP Subarray Leaf Node initialization "

# JSON keys
STR_KEY_DISH = "dish"
STR_KEY_RECEPTOR_ID_LIST = "receptorIDList"
STR_KEY_PB_ID_LIST = "processingBlockIdList"

PROP_DEF_VAL_TMCSP_MID_SALN = "ska_mid/tm_leaf_node/csp_subarray"
PROP_DEF_VAL_TMSDP_MID_SALN = "ska_mid/tm_leaf_node/sdp_subarray"
PROP_DEF_VAL_LEAF_NODE_PREFIX = "ska_mid/tm_leaf_node/d"
