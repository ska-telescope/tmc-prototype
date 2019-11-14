""" Python file containing String Variables for CSP Master Leaf Node"""

# Events
EVT_CBF_HEALTH = "cspCbfHealthState"
EVT_PSS_HEALTH = "cspPssHealthState"
EVT_PST_HEALTH = "cspPstHealthState"

#In/out commands
CMD_ON = "On"
CMD_OFF = "Off"
CMD_STANDBY = "Standby"
CMD_SET_CBF_ADMIN_MODE = "SetCbfAdminMode"
CMD_SET_PSS_ADMIN_MODE = "SetPssAdminMode"
CMD_SET_PST_ADMIN_MODE = "SetPstAdminMode"

# String constants
STR_CSP_CBF_HEALTH_OK = "CSP CBF health is OK."
STR_CSP_CBF_HEALTH_DEGRADED = "CSP CBF health is DEGRADED."
STR_CSP_CBF_HEALTH_FAILED = "CSP CBF health is FAILED."
STR_CSP_CBF_HEALTH_UNKNOWN = "CSP CBF health is UNKNOWN."
STR_CSP_PSS_HEALTH_OK = "CSP PSS health is OK."
STR_CSP_PSS_HEALTH_DEGRADED = "CSP PSS health is DEGRADED."
STR_CSP_PSS_HEALTH_FAILED = "CSP PSS health is FAILED."
STR_CSP_PSS_HEALTH_UNKNOWN = "CSP PSS health is UNKNOWN."
STR_CSP_PST_HEALTH_OK = "CSP PST health is OK."
STR_CSP_PST_HEALTH_DEGRADED = "CSP PST health is DEGRADED."
STR_CSP_PST_HEALTH_FAILED = "CSP PST health is FAILED."
STR_CSP_PST_HEALTH_UNKNOWN = "CSP PST health is UNKNOWN."

STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = " invoked successfully."
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "

STR_CSP_MASTER_LEAF_INIT_SUCCESS = "Csp Master Leaf Node initialized successfully."
STR_CSP_INIT_LEAF_NODE = "Initializing CSP Master Leaf Node ...."
STR_CSPMASTER_FQDN = "CspMasterFQDN :-> "
STR_FALSE = "False"
STR_DEV_ALARM = "The device is in ALARM state."
STR_CMD_FAILED = "CspMasterLeafNode_Commandfailed"
STR_CSP_CMD_CALLBK = "CspMasterLeafNode Command Callback"

# Error messages
ERR_INIT_PROP_ATTR = "Error on initialising properties and attributes "
ERR_IN_CREATE_PROXY = "Error in creating proxy of the device "
ERR_CSP_CBF_HEALTH_CB = "Error in CspCbfHealthCallback "
ERR_ON_SUBS_CSP_CBF_HEALTH = "Error in subscribing CspCbfHealth attribute "
ERR_CSP_PSS_HEALTH_CB = "Error in CspPssHealthCallback "
ERR_ON_SUBS_CSP_PSS_HEALTH = "Error in subscribing CspPssHealth attribute "
ERR_CSP_PST_HEALTH_CB = "Error in CspPstHealthCallback "
ERR_ON_SUBS_CSP_PST_HEALTH = "Error in subscribing CspPstHealth attribute "

ERR_SUBS_CSP_MASTER_LEAF_ATTR = "Exception occurred while subscribing to Csp Master attribute"

ERR_CSP_MASTER_LEAF_INIT = "Error occured in Csp Master Leaf Node initialization "
ERR_IN_CREATE_PROXY_CSP_MASTER = "Error in creating proxy to the CSP Master "
ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_MSG = "Error message is: "
ERR_ON_CMD = "Error in invoking command: ON"


#ENUMS
ENUM_HEALTH_OK, ENUM_HEALTH_DEGRADED, ENUM_HEALTH_FAILED, ENUM_HEALTH_UNKNOWN = list(range(0, 4))
ENUM_ADMIN_MODE_ONLINE, ENUM_ADMIN_MODE_OFFLINE, ENUM_ADMIN_MODE_MAINTENANCE, ENUM_ADMIN_MODE_NOT_FITTED, \
ENUM_ADMIN_MODE_RESERVED = list(range(0, 5))

#INTEGERS
INT_SKA_LEVEL = 3
