""" Python file containing String Variables for Dish Master"""

#string constants
ERR_MSG = "Error message is: \n"
STR_DISH_POINT_INPROG = "Dish is pointing towards the desired coordinates."
STR_DISH_POINT_SUCCESS = "Dish has pointed towards the desired coordinates."
STR_DISH_POINT_ALREADY = "Dish is already pointed towards the desired coordinates."
STR_DISH_STOW_SUCCESS = "Dish is stowed successfully."
STR_DISH_INIT_SUCCESS = "Dish Master is initialised successfully."
STR_DISH_STANDBYLP_MODE = "Dish is in STANDBY-LP mode."
STR_DISH_STANDBYFP_MODE = "Dish is in STANDBY-FP mode."
STR_DISH_MAINT_MODE = "Dish is in MAINTENANCE mode."
STR_DISH_OPERATE_MODE = "Dish is in OPERATE mode."
STR_SCAN_INPROG = "Scan in progress"
STR_DISH_NOT_READY = "Dish Pointing State is not READY."
STR_DATA_CAPTURE_STRT = "Data Capturing started."
STR_DISH_SLEW = "Dish is slewing"
STR_DATA_CAPTURE_STOP = "Data Capturing stopped."
STR_DATA_CAPTURE_ALREADY_STARTED = "Data Capuring is already in progress."
STR_DATA_CAPTURE_ALREADY_STOPPED = "Data Capuring is already stopped."
STR_FALSE = "False"
STR_ACHIEVED_POINTING = "Achieved Pointing"
STR_BREAK_LOOP = "Breaking a track while loop"
STR_TRACK_RECEIVED = "TRACK command is received on DishMaster"

STR_CMD_FAILED = "DishMaster_Commandfailed"
STR_SLEW_EXEC = "Slew command execution"
STR_SETSTANDBYFP_EXEC = "SetStandbyFPMode command execution"
STR_STOPCAPTURE_EXEC = "StopCapture command execution"
STR_STARTCAPTURE_EXEC = "StartCapture command execution"
STR_SCAN_EXEC = "Scan command execution"
STR_SET_OPERATEMODE_EXEC = "SetOperateMode command execution"
STR_SET_MAINTENANCEMODE_EXEC = "SetMaintenanceMode command execution"
STR_SET_STANDBYLPMODE_EXEC = "SetStandbyLPMode command execution"
STR_SET_STOWMODE_EXEC = "SetStowMode command execution"
STR_CONFIG_SUCCESS = "DishMaster configured successfully."
STR_CONFIG_DM_EXEC = "Configure command execution"
STR_POINTING = "pointing"
STR_AZ_THREAD_START= "Starting thread to change azimuth coordinates."
STR_EL_THREAD_START= "Starting thread to change elevation coordinates."
STR_DISH_RESTARTED = "Restart command excecuted succesfully."
STR_DISH_ABORT = "Abort command excecuted succesfully."
STR_DISH_OBSRESET = "ObsReset command excecuted succesfully."


#Error messages
ERR_EXE_POINT_FN = "Error in executing POINT function on Dish"
ERR_INIT_PROP_ATTR_DISH = "Error in initialising properties and attributes on Dish"
ERR_EXE_SET_STOW_MODE_CMD = "Error in executing SetStowMode Command on Dish"
ERR_EXE_SET_STNBYLP_MODE_CMD = "Error in executing SetStandbyLPMode Command on Dish"
ERR_EXE_SET_STNBYFP_MODE_CMD = "Error in executing SetStandbyFPMode Command on Dish"
ERR_EXE_SET_MAINT_MODE_CMD = "Error in executing SetMaintenanceMode Command on Dish"
ERR_EXE_SET_OPERATE_MODE_CMD = "Error in executing SetOperateMode Command on Dish"
ERR_EXE_SCAN_CMD = "Error in executing Scan Command on Dish"
ERR_EXE_STRT_CAPTURE_CMD = "Error in executing StartCapture Command on Dish"
ERR_EXE_STOP_CAPTURE_CMD = "Error in executing StopCapture Command on Dish"
ERR_EXE_SLEW_CMD = "Error in executing Slew Command on Dish"
ERR_INVALID_JSON = "Invalid JSON format."
ERR_JSON_KEY_NOT_FOUND = "JSON key not found."
ERR_CONFIG_DM = "Error occured in Dish Master."
ERR_EXE_ABORT_CMD = "Error in executing Abort Command on Dish"
ERR_EXE_RESTART_CMD = "Error in executing Restart Command on Dish"
ERR_EXE_OBSRESET_CMD = "Error in executing ObsReset Command on Dish"

THREAD_TRACK = "DishMaster"