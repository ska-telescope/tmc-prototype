""" Python file containing String Variables for CSP Master Leaf Node"""

# Events
EVT_CBF_HEALTH = "cspCbfHealthState"
EVT_PSS_HEALTH = "cspPssHealthState"
EVT_PST_HEALTH = "cspPstHealthState"

# In/out commands
CMD_TELESCOPE_ON = "Telescope On"
CMD_TELESCOPE_OFF = "Telescope Off"
CMD_TELESCOPE_STANDBY = "Telescope Standby"

# String constants
STR_INIT_SUCCESS = "CSP Master Leaf Node is initialized successfully."
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
STR_TELESCOPE_ON_CMD_ISSUED = "Telescope ON command invoked successfully from CSP Master leaf node."
STR_TELESCOPE_STANDBY_CMD_ISSUED = (
    "Telescope Standby command invoked successfully from CSP Master leaf node."
)
STR_TELESCOPE_OFF_CMD_ISSUED = "Telescope OFF command invoked successfully from CSP Master leaf node."
STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = "Command invoked successfully."
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "
STR_CSP_INIT_LEAF_NODE = "Initializing CSP Master Leaf Node ...."
STR_CSPMASTER_FQDN = "CspMasterFQDN :-> "
STR_DEV_ALARM = "The device is in ALARM state."
STR_CMD_FAILED = "CspMasterLeafNode_Commandfailed"
STR_TELESCOPE_ON_EXEC = "Telescope On command execution"
STR_OFF_EXEC = "Off command execution"
STR_TELESCOPE_STANDBY_EXEC = "Telescope Standby command execution"
STR_DEV_OFF = "The device is in OFF state."

# Error messages
ERR_IN_CREATE_PROXY = "Error in creating proxy of the device "
ERR_ON_SUBS_CSP_CBF_HEALTH = "Error in subscribing CspCbfHealth attribute "
ERR_ON_SUBS_CSP_PSS_HEALTH = "Error in subscribing CspPssHealth attribute "
ERR_ON_SUBS_CSP_PST_HEALTH = "Error in subscribing CspPstHealth attribute "
ERR_SUBS_CSP_MASTER_LEAF_ATTR = (
    "Exception occurred while subscribing to Csp Master attribute"
)
ERR_CSP_MASTER_LEAF_INIT = "Error occured in Csp Master Leaf Node initialization "
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_EXE_TELESCOPE_ON_CMD = "Error in executing Telescope On command"
ERR_EXE_OFF_CMD = "Error in executing Off command"
ERR_EXE_TELESCOPE_STANDBY_CMD = "Error in executing Telescope Standby command"
ERR_DEVFAILED_MSG = "This is error message for devfailed"
