# In/Out command constants
CMD_ASSIGN_RESOURCES = "AssignResources"
CMD_RELEASE_RESOURCES = "ReleaseAllResources"
CMD_RELEASE_MCCS_RESOURCES = "ReleaseResources"
CMD_ON = "On"
CMD_OFF = "Off"

# Event messages
EVT_UNKNOWN = "Event from the Unknown device!"
EVT_SUBSR_HEALTH_STATE = "healthState"
EVT_SUBSR_MCCS_MASTER_HEALTH = "mccsHealthState"

# Error messages
ERR_SUBSR_SA_HEALTH_STATE = "Error in subscribing Subarray healthState \n"
ERR_SUBSR_MCCS_MASTER_LEAF_HEALTH = (
    "Error in subscribing MCCS Master Leaf Node healthState \n"
)
ERR_INIT_PROP_ATTR_CN = (
    "Error on initialising properties and attributes on Central Node device."
)
ERR_IN_CREATE_PROXY = "Error in creating proxy of the LeafNode device: "
ERR_EXE_OFF_CMD = "Error in executing OFF Telescope command "
ERR_EXE_ON_CMD = "Error in executing STARTUP(ON) Telescope command "
ERR_INVALID_JSON = "Invalid JSON format"
ERR_JSON_KEY_NOT_FOUND = "JSON key not found"
ERR_RELEASE_RESOURCES_CMD = "Error occured while releasing resources "
ERR_SUBARRAY_HEALTHSTATE = (
    "Key Error occurred while setting Subarray healthState"
)
ERR_ASSGN_RESOURCES = (
    "Error occurred while assigning resources to the Subarray \n"
)
ERR_RELEASE_RESOURCES = (
    "Error occurred while releasing resources from the Subarray \n"
)
ERR_HEALTH_STATE_CB = "Error handling healthState callback for evt: %s"
ERR_STANDBY_CMD_INCOMPLETE = "StandByTelescope command is not completed yet"
ERR_STARTUP_CMD_INCOMPLETE = "StartUpTelescope command is not completed yet"
ERR_SUB_CMD_RES_ATTR = "Error on subscribing commandResult attribute"

# General strings
STR_HEALTH_STATE = "healthState of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = (
    "Subarray healthState event returned unknown value \n"
)
STR_ERR_MSG = "Error message is: "
STR_STANDBY_CMD_ISSUED = (
    "STANDBYTELESCOPE command invoked from Central node Low"
)
STR_ON_CMD_ISSUED = (
    "STARTUPTELESCOPE (ON) command invoked from Central node Low"
)
STR_INIT_SUCCESS = "CentralNode is initialized successfully."
STR_FALSE = "False"
STR_ASSIGN_RESOURCES_SUCCESS = "Resources are assigned successfully"
STR_FALSE_TAG = "False in ReleaseALL tag is not yet supported"
STR_REL_RESOURCES = "Resources have been released successfully"
STR_CMD_FAILED = "CentralNode_CommandFailed"
STR_RELEASE_RES_EXEC = "RELEASERESOURCES command execution"
STR_ASSIGN_RES_EXEC = "ASSIGNRESOURCES command execution"
STR_ON_EXEC = "STARTUPTELESCOPE (ON) command execution"
STR_STANDBY_EXEC = "STANDBYTELESCOPE command execution"
STR_RESOURCE_ALLOCATION_FAILED = "Resource allocation failed."
STR_CMD_OFF_MCCSMLN_DEV = "OFF command invoked on MccsMasterLeafNode device "
STR_CMD_OFF_SA_LOW_DEV = "OFF command invoked on SubarrayNode device"
STR_CMD_ON_MCCS_DEV = "ON command invoked on MccsMasterLeafNode device"
STR_CMD_ON_SA_LOW_DEV = "ON command invoked on SubarrayNode device"
STR_CN_INIT_SUCCESS = "Central Node initialised successfully."
STR_RETURN_MSG_ASSIGN_RESOURCES_SUCCESS = (
    "AssignResources Command invoked successfully on CentralNodeLow."
)
STR_RETURN_MSG_RELEASE_RESOURCES_SUCCESS = (
    "ReleaseResources Command invoked successfully on CentralNodeLow."
)

# PROPERTIES DEFAULT VALUES
PROP_DEF_VAL_TM_LOW_SA1 = "ska_low/tm_subarray_node/1"
