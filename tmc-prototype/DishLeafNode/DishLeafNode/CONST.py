#Events
EVT_DISH_MODE = "dishMode"
EVT_DISH_POINTING_STATE = "pointingState"
EVT_DISH_CAPTURING = "capturing"
EVT_ACHVD_POINT = "achievedPointing"
EVT_DESIRED_POINT = "desiredPointing"

#In/out commands
CMD_SET_STOW_MODE = "SetStowMode"
CMD_SET_STANDBYLP_MODE = "SetStandbyLPMode"
CMD_SET_OPERATE_MODE = "SetOperateMode"
CMD_SET_STANDBYFP_MODE = "SetStandbyFPMode"
CMD_DISH_SCAN = "Scan"
CMD_DISH_SLEW = "Slew"
CMD_STOP_CAPTURE = "StopCapture"
CMD_START_CAPTURE = "StartCapture"

#string constants
STR_DISH_STANDBYLP_MODE = "Dish is in STANDBY-LP mode."
STR_DISH_STANDBYFP_MODE = "Dish is in STANDBY-FP mode."
STR_DISH_MAINT_MODE = "Dish is in MAINTENANCE mode."
STR_DISH_OPERATE_MODE = "Dish is in OPERATE mode."
STR_DISH_STARTUP_MODE = "Dish is in STARTUP mode."
STR_DISH_SHUTDOWN_MODE = "Dish is in SHUTDOWN mode."
STR_DISH_STOW_MODE = "Dish is in STOW mode."
STR_DISH_CONFIG_MODE = "Dish is in CONFIG mode."
STR_DISH_OFF_MODE = "Dish is in OFF mode."
STR_DISH_UNKNOWN_MODE = "Dish Mode :-> UNKNOWN!\n"

STR_DISH_POINT_STATE_READY = "Dish Pointing State :-> READY"
STR_DISH_POINT_STATE_SLEW = "Dish Pointing State :-> SLEWING"
STR_DISH_POINT_STATE_TRACK = "Dish Pointing State :-> TRACKING"
STR_DISH_POINT_STATE_SCAN = "Dish Pointing State :-> SCANNING"
STR_DISH_POINT_STATE_UNKNOWN = "Dish is in UNKNOWN pointing state!\n"

STR_DISH_HEALTH_STATE_OK = "Dish Health state :-> OK"
STR_DISH_HEALTH_STATE_DEGRADED = "Dish Health state :-> DEGRADED"
STR_DISH_HEALTH_STATE_FAILED = "Dish Health state :-> FAILED"
STR_DISH_HEALTH_STATE_UNKNOWN = "Dish Health state :-> UNKNOWN"
STR_DISH_HEALTH_STATE_ERR = "Error: Dish Health state :-> "

STR_DISH_CAPTURING_TRUE = "Dish data capturing :-> TRUE"
STR_DISH_CAPTURING_FALSE = "Dish data capturing :-> FALSE"
STR_DISH_CAPTURING_UNKNOWN = "Dish date capturing :-> UNKNOWN!\n"

STR_ACHIEVED_POINTING = "Achieved Pointing :-> "
STR_DESIRED_POINTING = "Desired Pointing :-> "

STR_INIT_LEAF_NODE = "Initializing Leaf Node..."

STR_DISHMASTER_FQN = "DishMasterFQDN :-> "
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "

STR_DISH_INIT_SUCCESS = "Dish Leaf Node initialized successfully."

STR_COMMAND = "Command :->"
STR_INVOKE_SUCCESS = "invoked successfully."
STR_IN_SCAN = "in scan"
STR_OUT_SCAN = "out scan"

#error messages
ERR_DISH_MODE_CB = "Unexpected error in DishModeCallback!"
ERR_ON_SUBS_DISH_MODE_ATTR = "Error event on subscribing DishMode attribute!"

ERR_DISH_POINT_STATE_CB = "Unexpected error in DishPointingStateCallback!"
ERR_ON_SUBS_DISH_POINT_ATTR = "Error event on subscribing DishPointing attribute!"

ERR_DISH_POINT_STATE_UNKNOWN = "Dish is in UNKNOWN pointing state!\n"

ERR_DISH_HEALTH_STATE_CB = "Unexpected error in DishHealthStateCallback!"
ERR_SUBSR_DISH_HEALTH_STATE = "Error event on subscribing Dish HealthState attribute!\n"


ERR_DISH_CAPTURING_CB = "Unexpected error in DishCapturingCallback!"
ERR_SUBSR_CAPTURING_ATTR = "Error event on subscribing Capturing attribute!\n"

ERR_DISH_ACHVD_POINT = "Unexpected error in DishAchievedPointingCallback!"
ERR_ON_SUBS_DISH_ACHVD_ATTR = "Error event on subscribing AchievedPointing attribute!"

ERR_DISH_DESIRED_POINT = "Unexpected error in DishDesiredPointingCallback!"
ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR = "Error event on subscribing DesiredPointing attribute!"

ERR_EXCEPT_CMD_CB = "Exception in CommandCallback!: \n"
ERR_INVOKING_CMD = "Error in invoking command:"

ERR_IN_CREATE_PROXY_DM = "Unexpected error in creating proxy to the Dish Master "
ERR_SUBS_DISH_ATTR = "Exception occurred while subscribing to Dish attributes"

ERR_DISH_INIT = "Error occured in Dish Leaf Node initialization!"

ERR_EXE_STOW_CMD = "Exception in executing STOW command "
ERR_EXE_STANDBYLP_CMD = "Exception occurred in SetStandByLPMode command."
ERR_EXE_SET_OPER_MODE_CMD = "Exception in SetOperateMode command:\n"
ERR_EXE_SCAN_CMD = "Exception in executing SCAN command "
ERR_EXE_END_SCAN_CMD = "Exception in EndScan command:\n"
ERR_EXE_CONFIGURE_CMD = "Exception occurred in Configure command."
ERR_EXE_START_CAPTURE_CMD = "Exception occurred in StartCapture command."
ERR_EXE_STOP_CAPTURE_CMD = "Exception occurred in StopCapture command."
ERR_EXE_STANDBYFP_CMD = "Exception occurred in SetStandbyFPMode command."
ERR_EXE_SLEW_CMD = "Exception occurred in Slew command."

