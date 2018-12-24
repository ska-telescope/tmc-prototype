# In/Out command constants
CMD_SET_STOW_MODE = "SetStowMode"
CMD_SET_STANDBY_MODE = "SetStandbyLPMode"
CMD_SET_OPERATE_MODE = "SetOperateMode"



#Event messages
EVT_SA1_NODE = "tm_subarray_node/1"
EVT_SA2_NODE = "tm_subarray_node/2"
EVT_UNKNOWN_SA = "Event from the Unknown Subarray device!"
EVT_SUBSR_SA_HEALTH_STATE = "healthState"
#
#Error messages
ERR_AGGR_HEALTH_STATE = "Unexpected error while aggregating Health state!\n"
ERR_SUBSR_SA_HEALTH_STATE = "Error event on subscribing Subarray HealthState!\n"
ERR_INIT_PROP_ATTR_CN = "Unexpected error on initialising properties and attributes " \
                        "on Central Node device."
ERR_IN_READ_DISH_LN_DEVS = "Unexpected error in reading exported Dish Leaf Node device names " \
                           "from database \n"
ERR_IN_CREATE_PROXY = "Unexpected error in creating proxy of the device "
ERR_EXE_STOW_CMD = "Unexpected error in executing STOW command "
ERR_EXE_STANDBY_CMD = "Unexpected error in executing STANDBY Telescope command "
ERR_EXE_STARTUP_CMD = "Unexpected error in executing STARTUP Telescope command "


#strings
#General strings
STR_HEALTH_STATE = "Health state of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = "Subarray Health state event returned unknown value! \n"
STR_ERR_MSG = "Error message is: \n"
STR_STOW_CMD_ISSUED_CN = "STOW command invoked from Central node on the requested dishes"
STR_STANDBY_CMD_ISSUED = "StandByTelescope command invoked from Central node"
STR_STARTUP_CMD_ISSUED = "StartUpTelescope command invoked from Central node"


#PROPERTIES DEFAULT VALUES
PROP_DEF_VAL_TM_MID_SA1 = "ska_mid/tm_subarray_node/1"
PROP_DEF_VAL_TM_MID_SA2 = "ska_mid/tm_subarray_node/2"
PROP_DEF_VAL_LEAF_NODE_PREFIX = "ska_mid/tm_leaf_node/d"

GET_DEVICE_LIST_TANGO_DB = "ska_mid/tm_leaf_node/d000*"



ENUM_LAB_OK = "OK"
ENUM_LAB_DEGRADED = "DEGRADED"
ENUM_LAB_FAILED = "FAILED"
ENUM_LAB_UNKNOWN = "UNKNOWN"

#ENUMS
ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = range(0, 4)

#INTEGERS
INT_SKA_LEVEL = 1

#