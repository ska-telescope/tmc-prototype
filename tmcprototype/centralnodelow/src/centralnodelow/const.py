# In/Out command constants
CMD_SET_STOW_MODE = "SetStowMode"
CMD_SET_STANDBY_MODE = "SetStandbyLPMode"
CMD_SET_OPERATE_MODE = "SetOperateMode"
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseAllResources"

CMD_STANDBY = "Standby"
STR_CMD_STANDBY_CSP_DEV = "STANDBY command invoked on CspMasterLeafNode device "
STR_CMD_STANDBY_SDP_DEV = "STANDBY command invoked on SdpMasterleafNode device "
STR_CMD_STANDBY_SA_DEV = "STANDBY command invoked on SubarrayNode device"
CMD_ON = "On"
CMD_OFF = "Off"
STR_CMD_ON_MCCS_DEV = "ON command invoked on MccsMasterLeafNode device"
STR_CMD_ON_SA_LOW_DEV = "ON command invoked on SubarrayNodeLow device"

#Event messages
EVT_UNKNOWN = "Event from the Unknown device!"
EVT_SUBSR_HEALTH_STATE = "healthState"
EVT_SUBSR_OBS_STATE = "obsState"
EVT_SUBSR_MCCS_MASTER_HEALTH = "mccsHealthState"

#Error messages
ERR_AGGR_OBS_STATE = "Error in Subarray obsState callback \n"
ERR_SUBSR_SA_HEALTH_STATE = "Error in subscribing Subarray healthState \n"
ERR_SUBSR_SA_OBS_STATE = "Error in subscribing Subarray obsState \n"
ERR_SUBSR_MCCS_MASTER_LEAF_HEALTH = "Error in subscribing MCCS Master Leaf Node healthState \n"
ERR_INIT_PROP_ATTR_CN = "Error on initialising properties and attributes " \
                        "on Central Node device."
ERR_IN_READ_DISH_LN_DEVS = "Error in reading exported Dish Leaf Node device names " \
                           "from database \n"
ERR_IN_CREATE_PROXY = "Error in creating proxy of the LeafNode device: "
ERR_EXE_STOW_CMD = "Error in executing STOW command "
ERR_EXE_STANDBY_CMD = "Error in executing STANDBY Telescope command "
ERR_EXE_OFF_CMD = "Error in executing OFF Telescope command "
ERR_EXE_ON_CMD = "Error in executing STARTUP(ON) Telescope command "
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found "
ERR_RELEASE_RESOURCES_CMD = "Error occured while releasing resources "
ERR_SUBARRAY_HEALTHSTATE = "Key Error occurred while setting Subarray healthState"
ERR_ASSGN_RESOURCES = "Error occurred while assigning resources to the Subarray \n"
ERR_RELEASE_RESOURCES = "Error occurred while releasing resources from the Subarray \n"
ERR_STOW_ARGIN = "Invalid StowAntennas arguments \n"
ERR_HEALTH_STATE_CB = "Error handling healthState callback for evt: %s"
ERR_SUBARRAY_ID_DOES_NOT_EXIST = "The Subarray '99' does not exist."
ERR_RECEPTOR_ID_DOES_NOT_EXIST = "The following Receptor id(s) do not exist:"
ERR_RECEPTOR_ID_REALLOCATION = "The following Receptor id(s) are allocated to other subarrays: "

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
STR_STANDBY_CMD_ISSUED = "STANDBYTELESCOPE command invoked from Central node"
STR_ON_CMD_ISSUED = "STARTUPTELESCOPE (ON) command invoked from Central node"
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
STR_STOW_ANTENNA_EXEC = "STOW_ANTENNAS command execution"
STR_RELEASE_RES_EXEC = "RELEASERESOURCES command execution"
STR_ASSIGN_RES_EXEC = "ASSIGNRESOURCES command execution"
STR_ON_EXEC = "STARTUPTELESCOPE (ON) command execution"
STR_STANDBY_EXEC = "STANDBYTELESCOPE command execution"
STR_RESOURCE_ALLOCATION_FAILED = "Resource allocation failed."

#PROPERTIES DEFAULT VALUES
PROP_DEF_VAL_TM_MID_SA1 = "ska_mid/tm_subarray_node/1"
PROP_DEF_VAL_TM_MID_SA2 = "ska_mid/tm_subarray_node/2"
PROP_DEF_VAL_TM_MID_SA3 = "ska_mid/tm_subarray_node/3"
PROP_DEF_VAL_LEAF_NODE_PREFIX = "ska_mid/tm_leaf_node/d"
GET_DEVICE_LIST_TANGO_DB = "ska_mid/tm_leaf_node/d000*"


#INTEGERS
INT_SKA_LEVEL = 1
