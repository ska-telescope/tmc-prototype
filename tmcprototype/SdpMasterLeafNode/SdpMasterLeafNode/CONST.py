# """ Python file containing String Variables for CSP Master Leaf Node"""
#
# # Events
#
# In/out commands
CMD_ON = "On"
# CMD_OFF = "Off"
CMD_STANDBY = "Standby"

# # String constants
STR_INIT_SUCCESS = "SDP Master Leaf Node is initialized successfully."
STR_SDPMASTER_FQDN = "SdpMasterFQDN :-> "
ERR_IN_CREATE_PROXY = "Error in creating proxy of the device "
STR_FALSE = "False"
STR_TRUE = "True"
STR_SDP_MASTER_FQDN = "mid-sdp/elt/master"
STR_OFF_CMD_SUCCESS = "SdpMasterLeafNode.Off command executed successfully."
STR_DISABLE_CMS_SUCCESS = "SdpMasterLeafNode.Disable command executed successfully."
STR_SETTING_CB_MODEL = "Setting CallBack Model as :-> "
STR_COMMAND = "Command :-> "
STR_INVOKE_SUCCESS = " invoked successfully."
STR_CMD_FAILED = "SdpSubarray_Commandfailed"
STR_SDP_CMD_CALLBK = "SdpMasterLeafNode Command Callback"
#
#
# Error messages
ERR_INIT_PROP_ATTR = "Error on initialising properties and attributes "
ERR_MSG = "Error message is: "
ERR_IN_CREATE_PROXY_SDP_MASTER = "Error in creating proxy to the SDP Master "
ERR_INVOKING_CMD = "Error in invoking command: "
ERR_EXCEPT_CMD_CB = "Exception in CommandCallback: \n"
ERR_OFF_CMD_FAIL = "Error in invoking off command."

#ENUMS
ENUM_STATE_INIT, ENUM_STANDBY, ENUM_DISABLE, ENUM_ON, ENUM_ALARM, ENUM_FAULT, ENUM_UNKNOWN = list(range(0, 7))
ENUM_ADMIN_MODE_ONLINE, ENUM_ADMIN_MODE_OFFLINE, ENUM_ADMIN_MODE_MAINTENANCE, ENUM_ADMIN_MODE_NOT_FITTED, \
ENUM_ADMIN_MODE_RESERVED = list(range(0, 5))
ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = list(range(0, 4))

# INTEGERS

