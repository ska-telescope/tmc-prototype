"""
This file is part of the DishLeafNode project and defines variables used
"""

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
CMD_DISH_CONFIGURE = 'Configure'
CMD_STOP_CAPTURE = "StopCapture"
CMD_START_CAPTURE = "StartCapture"
CMD_TRACK = "Track"
CMD_STOP_TRACK = "StopTrack"
CMD_ABORT = "Abort"
CMD_RESTART = "Restart"

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
STR_DISH_UNKNOWN_MODE = "Dish Mode :-> UNKNOWN\n"

STR_DISH_CAPTURING_TRUE = "Dish data capturing :-> TRUE"
STR_DISH_CAPTURING_FALSE = "Dish data capturing :-> FALSE"
STR_DISH_CAPTURING_UNKNOWN = "Dish date capturing :-> UNKNOWN\n"

STR_ACHIEVED_POINTING = "Achieved Pointing :-> "
STR_DESIRED_POINTING = "Desired Pointing :-> "

STR_INIT_LEAF_NODE = "Initializing Leaf Node..."

STR_DISHMASTER_FQDN = "DishMasterFQDN :-> "
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "

STR_DISH_INIT_SUCCESS = "Dish Leaf Node initialized successfully."

STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = " invoked successfully."
STR_IN_SCAN = "in scan"
STR_OUT_SCAN = "out scan"
STR_FALSE = "False"
STR_OK = "OK"


#error messages
ERR_DISH_MODE_CB = "Error in DishModeCallback "
ERR_ON_SUBS_DISH_MODE_ATTR = "Error in subscribing DishMode attribute "

ERR_DISH_POINT_STATE_CB = "Error in DishPointingStateCallback "
ERR_ON_SUBS_DISH_POINT_ATTR = "Error in subscribing DishPointing attribute "

ERR_DISH_POINT_STATE_UNKNOWN = "Dish is in UNKNOWN pointing state \n"

ERR_DISH_HEALTH_STATE_CB = "Error in DishHealthStateCallback "
ERR_SUBSR_DISH_HEALTH_STATE = "Error in subscribing Dish HealthState attribute \n"

ERR_DISH_CAPTURING_CB = "Error in DishCapturingCallback "
ERR_SUBSR_CAPTURING_ATTR = "Error in subscribing Capturing attribute \n"

ERR_DISH_ACHVD_POINT = "Error in DishAchievedPointingCallback "
ERR_ON_SUBS_DISH_ACHVD_ATTR = "Error in subscribing AchievedPointing attribute "

ERR_DISH_DESIRED_POINT = "Error in DishDesiredPointingCallback "
ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR = "Error in subscribing DesiredPointing attribute "

ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_INVOKING_CMD = "Error in invoking command: "

ERR_IN_CREATE_PROXY_DM = "Error in creating proxy to the Dish Master "
ERR_SUBS_DISH_ATTR = "Exception occurred while subscribing to Dish attributes"

ERR_DISH_INIT = "Error occured in Dish Leaf Node initialization "

ERR_EXE_STOW_CMD = "Exception in executing STOW command "
ERR_EXE_STANDBYLP_CMD = "Exception occurred in SetStandByLPMode command."
ERR_EXE_SET_OPER_MODE_CMD = "Exception in SetOperateMode command:\n"
ERR_EXE_SCAN_CMD = "Exception in executing SCAN command"
ERR_EXE_END_SCAN_CMD = "Exception in EndScan command"
ERR_EXE_CONFIGURE_CMD = "Exception occurred in Configure command"
ERR_EXE_START_CAPTURE_CMD = "Exception occurred in StartCapture command"
ERR_EXE_STOP_CAPTURE_CMD = "Exception occurred in StopCapture command"
ERR_EXE_STOP_TRACK_CMD = "Exception occurred in StopTrack command"
ERR_EXE_STANDBYFP_CMD = "Exception occurred in SetStandbyFPMode command"
ERR_EXE_SLEW_CMD = "Exception occurred in Slew command"
ERR_RADEC_TO_AZEL = "Exception occurred in Ra-Dec to Az-El conversion "
ERR_INVALID_DATATYPE = " Invalid argument "
ERR_RADEC_TO_AZEL_VAL_ERR = "Value Error in Ra-Dec to Az-El conversion"
ERR_ELE_LIM = "Minimum elevation limit has been reached."
ERR_TIME_LIM = "Tracking duration is complete."
ERR_EXE_TRACK = "Exception occured in the execution of Track command."
ERR_EXE_ABORT_CMD = "Exception occurred in Abort command"
ERR_EXE_RESTART_CMD = "Exception occurred in Restart command"

# commands success string
STR_SET_STOW_MODE_SUCCESS = "SETSTOWMODE command invoked on DishLeafNode device."
STR_SETSTANDBYLP_SUCCESS = "STANDBYLPMODE command invoked on DishLeafNode device."
STR_SETOPERATE_SUCCESS = "STOPCAPTURE command invoked on DishLeafNode device."
STR_CONFIGURE_SUCCESS = "CONFIGURE command invoked on DishLeafNode device."
STR_SCAN_SUCCESS = "SCAN command invoked on DishLeafNode device."
STR_ENDSCAN_SUCCESS = "ENDSCAN command invoked on DishLeafNode device."
STR_STARTCAPTURE_SUCCESS = "STARTCAPTURE command invoked on DishLeafNode device."
STR_STOPCAPTURE_SUCCESS = "STOPCAPTURE command invoked on DishLeafNode device."
STR_STANDBYFP_SUCCESS = "SETSTANDBYFP command invoked on DishLeafNode device."
STR_SLEW_SUCCESS = "SLEW command invoked on DishLeafNode device."
STR_TRACK_SUCCESS = "TRACK command invoked on DishLeafNode device."
STR_STOP_TRACK_SUCCESS = "STOPTRACK command invoked on DishLeafNode device."
STR_ABORT_SUCCESS = "ABORT command invoked successfully on DishLeafNode device."
STR_RESTART_SUCCESS = "RESTART command invoked successfully on DishLeafNode device."

STR_CMD_FAILED = "DishLeafNode_Commandfailed"
STR_SLEW_EXEC = "Slew command execution"
STR_STOPCAPTURE_EXEC = "StopCapture command execution"
STR_TRACK_EXEC = "Track command execution"
STR_STOPTRACK_EXEC = "StopTrack command execution"
STR_STARTCAPTURE_EXEC = "StartCapture command execution"
STR_CONFIGURE_EXEC = "Configure command execution"
STR_ENDSCAN_EXEC = "EndScan command execution"
STR_SCAN_EXEC = "Scan command execution"
STR_CMD_CALLBK = "DishLeafNode Command Callback"
STR_ABORT_EXEC = "Abort command execution"
STR_RESTART_EXEC = "Restart command execution"

THREAD_TRACK = "DishLeafNode"
ERR_INVALID_JSON = "Invalid JSON format."
ERR_JSON_KEY_NOT_FOUND = "JSON key not found."