
"""
This file is part of the SubarrayNode project and defines variables used
"""
#Events
EVT_DISH_HEALTH_STATE = "dishHealthState"

#Commands
CMD_SCAN = "Scan"
CMD_CONFIGURE = "Configure"
CMD_END_SCAN = "EndScan"
CMD_TRACK = "Track"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_ALL_RESOURCES = "ReleaseAllResources"


#GROUPS
GRP_DISH_LEAF_NODE = "DishLeafNode_Group"

#strings
STR_SCAN_IP_ARG = "Scan inputs Arguments :-> "
STR_GRP_DEF_SCAN_FN = "Group Definitions in scan function :-> "
STR_SA_SCANNING = "Subarray is scanning at the desired pointing coordinates."

STR_GRP_DEF_END_SCAN_FN = "Group Definitions in EndScan function :-> "
STR_SCAN_COMPLETE = "Scan is completed"
STR_TEST_DEV_VS_EVT_ID = "self.testDeviceVsEventID "
STR_GRP_DEF = "Group definition :-> "
STR_LN_PROXIES = "LeafNode proxies :-> "
STR_SUBS_HEALTH_ST_LN = "Subscribing healthState attributes of Leaf Nodes..."
STR_HS_EVNT_ID = "DishHealth EventID array is:"

STR_ASSIGN_RES_SUCCESS = "Receptors are assigned successfully."
STR_DISH_PROXY_LIST = "Dishproxy list"
STR_HEALTH_ID = "health id "

STR_RECEPTORS_REMOVE_SUCCESS = "All the receptors are removed from the Subarray node."
STR_HEALTH_STATE = "healthState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = "Subarray healthState event returned unknown value  \n"

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
RESRC_ALREADY_RELEASED = "Resources are already released from Subarray"
STR_FALSE = "False"
STR_OK = "OK"
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

#Error messages
ERR_SCAN_CMD = "Exception in Scan command: "
ERR_END_SCAN_CMD = "Exception in End Scan command:"
ERR_ASSIGN_RES_CMD = "Exception in AssignResources command: "
ERR_RELEASE_RES_CMD = "Exception occurred in ReleaseAllResources command."
ERR_AGGR_HEALTH_STATE = "Error while aggregating healthState \n"
ERR_SUBSR_SA_HEALTH_STATE = "Error in subscribing Subarray healthState \n"
ERR_CONFIGURE_CMD = "Exception in Configure command: \n "
ERR_ADDING_LEAFNODE = "Exception occurred while adding LeafNodes "
ERR_END_SCAN_CMD_ON_GROUP = "Error invoking EndScan command on DishLeafNode group"
ERR_RELEASE_RES_CMD_GROUP = "Error invoking AssignResources command on DishLeafNode group"
ERR_SETHEALTH_CALLBK = "KeyError occurred in setHealth callback of SubarrayNode "
ERR_CONFIGURE_CMD_GROUP = "Error invoking Configure command on DishLeafNode group "
ERR_INVALID_DATATYPE = " Invalid argument "
ERR_DUPLICATE_END_SCAN_CMD = "End Scan Command Already Executed"
ERR_DUPLICATE_SCAN_CMD = "Scan Command Already Executed"
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_TRACK_CMD = "Exception in Track command: \n "
ERR_CSP_CMD = "Failed to send command to CSP Subarray Leaf Node"
ERR_SDP_CMD = "Failed to send command to SDP Subarray Leaf Node"

#ENUMS
ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = list(range(0, 4))

# JSON keys
STR_KEY_DISH = "dish"
STR_KEY_RECEPTOR_ID_LIST = "receptorIDList"
STR_KEY_PB_ID_LIST = "processingBlockIdList"