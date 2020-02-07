# In/Out command constants
CMD_SET_STOW_MODE = "SetStowMode"
CMD_SET_STANDBY_MODE = "SetStandbyLPMode"
CMD_SET_OPERATE_MODE = "SetOperateMode"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseAllResources"

CMD_STANDBY = "Standby"
CMD_STARTUP = "On"

#Event messages
EVT_UNKNOWN = "Event from the Unknown device!"
EVT_SUBSR_HEALTH_STATE = "healthState"
EVT_SUBSR_CSP_MASTER_HEALTH = "cspHealthState"
EVT_SUBSR_SDP_MASTER_HEALTH = "sdpHealthState"
EVT_SUBSR_SA_RECEPTOR_ID_LIST = "receptorIDList"

#Error messages
ERR_AGGR_HEALTH_STATE = "Error while aggregating Subarray healthState \n"
ERR_SUBSR_SA_HEALTH_STATE = "Error in subscribing Subarray healthState \n"
ERR_SUBSR_CSP_MASTER_LEAF_HEALTH = "Error in subscribing CSP Master Leaf Node healthState \n"
ERR_SUBSR_SDP_MASTER_LEAF_HEALTH = "Error in subscribing SDP Master Leaf Node healthState \n"
ERR_INIT_PROP_ATTR_CN = "Error on initialising properties and attributes " \
                        "on Central Node device."
ERR_IN_READ_DISH_LN_DEVS = "Error in reading exported Dish Leaf Node device names " \
                           "from database \n"
ERR_IN_CREATE_PROXY = "Error in creating proxy of the LeafNode device: "
ERR_EXE_STOW_CMD = "Error in executing STOW command "
ERR_EXE_STANDBY_CMD = "Error in executing STANDBY Telescope command "
ERR_EXE_STARTUP_CMD = "Error in executing STARTUP Telescope command "
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_RELEASE_RESOURCES_CMD = "Error occured while releasing resources "
ERR_SUBARRAY_HEALTHSTATE = "Key Error occurred while setting Subarray healthState"
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the Subarray \n"
ERR_RELEASE_RESOURCES = "Error occurred while releasing resources from the Subarray \n"
ERR_STOW_ARGIN = "Invalid StowAntennas arguments \n"

#strings
#General strings
STR_HEALTH_STATE = "healthState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = "Subarray healthState event returned unknown value \n"
STR_ERR_MSG = "Error message is: "
STR_STOW_CMD_ISSUED_CN = "STOW command invoked from Central node on the requested dishes"
STR_STANDBY_CMD_ISSUED = "StandByTelescope command invoked from Central node"
STR_STARTUP_CMD_ISSUED = "StartUpTelescope command invoked from Central node"
STR_INIT_SUCCESS = "CentralNode is initialized successfully."
STR_FALSE = "False"
STR_DISH_DUPLICATE = "List of the dishes that are already allocated: "
STR_ASSIGN_RESOURCES_SUCCESS = "Resources are assigned successfully"
STR_FALSE_TAG = "False in ReleaseALL tag is not yet supported"
STR_REL_RESOURCES = "Resources have been released successfully"
STR_ALL_RES_NOT_REL = "All the resources are not released"
STR_LIST_RES_NOT_REL = "List of the resources that are not released:"
STR_CSP_CBF_DEV_NAME = "mid_csp_cbf/sub_elt/master"
STR_CMD_FAILED = "CentralNode_CommandFailed"
STR_STOW_ANTENNA_EXEC = "StowAntennas command execution"
STR_RELEASE_RES_EXEC = "ReleaseResources command execution"
STR_ASSIGN_RES_EXEC = "AssignResources command execution"
STR_STARTUP_EXEC = "StartUpTelescope command execution"
STR_STANDBY_EXEC = "StandByTelescope command execution"

#PROPERTIES DEFAULT VALUES
PROP_DEF_VAL_TM_MID_SA1 = "ska_mid/tm_subarray_node/1"
PROP_DEF_VAL_TM_MID_SA2 = "ska_mid/tm_subarray_node/2"
PROP_DEF_VAL_TM_MID_SA3 = "ska_mid/tm_subarray_node/3"
PROP_DEF_VAL_LEAF_NODE_PREFIX = "ska_mid/tm_leaf_node/d"
GET_DEVICE_LIST_TANGO_DB = "ska_mid/tm_leaf_node/d000*"
ENUM_LAB_OK = "OK"
ENUM_LAB_DEGRADED = "DEGRADED"
ENUM_LAB_FAILED = "FAILED"
ENUM_LAB_UNKNOWN = "UNKNOWN"

#ENUMS
# healthState
ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = list(range(0, 4))
# adminMode
ENUM_ONLINE, ENUM_OFFLINE, ENUM_MAINTENANCE, ENUM_NOTFITTED, ENUM_RESERVED = list(range(0, 5))
#INTEGERS
INT_SKA_LEVEL = 1
