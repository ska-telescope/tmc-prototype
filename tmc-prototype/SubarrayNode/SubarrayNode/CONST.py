
#Events
EVT_DISH_HEALTH_STATE = "dishHealthState"


#Commands
CMD_SCAN = "Scan"
CMD_CONFIGURE = "Configure"
CMD_END_SCAN = "EndScan"

#GROUPS
GRP_DISH_LEAF_NODE = "DishLeafNode_Group"

#strings
STR_SCAN_IP_ARG = "Scan inputs Arguments :-> "
STR_GRP_DEF_SCAN_FN = "Group Definitions in scan function :-> "
STR_SA_SCANNING = "Subarray is scanning at the desired pointing coordinates."

STR_GRP_DEF_END_SCAN_FN ="Group Definitions in EndScan function :-> "
STR_SCAN_COMPLETE = "Scan is completed"
STR_TEST_DEV_VS_EVT_ID = "self.testDeviceVsEventID "
STR_GRP_DEF = "Group definition :-> "
STR_LN_PROXIES = "LeafNode proxies :-> "
STR_SUBS_HEALTH_ST_LN = "Subscribing HealthState attributes of Leaf Nodes..."
STR_HS_EVNT_ID = "DishHealth EventID array is:"

STR_ASSIGN_RES_SUCCESS = "Receptors are assigned successfully."
STR_DISH_PROXY_LIST = "Dishproxy list"
STR_HEALTH_ID = "health id "

STR_RECEPTORS_REMOVE_SUCCESS = "All the receptors are removed from the Subarray node."
STR_HEALTH_STATE = "Health state of "
STR_OK = " :-> OK"
STR_DEGRADED = " :-> DEGRADED"
STR_FAILED = " :-> FAILED"
STR_UNKNOWN = " :-> UNKNOWN"
STR_HEALTH_STATE_UNKNOWN_VAL = "Subarray Health state event returned unknown value! \n"

STR_SA_INIT = "Initializing SubarrayNode..."
STR_SA_INIT_SUCCESS = "Subarray node is initialized successfully."

STR_CONFIGURE_IP_ARG = "Input Arguments for Configure command :-> "
STR_GRP_DEF_CONFIGURE_FN = "Group Definitions during Configure command :-> "

STR_CONFIGURE_CMD_INVOKED_SA = "Configure command invoked on Subarray"


#Error messages
ERR_SCAN_CMD = "Exception in Scan command:"
ERR_END_SCAN_CMD = "Exception in End Scan command:"
ERR_ASSIGN_RES_CMD = "Exception in AssignResources command:"
ERR_RELEASE_RES_CMD = "Exception occurred in ReleaseAllResources command."
ERR_AGGR_HEALTH_STATE = "Unexpected error while aggregating Health state!\n"
ERR_SUBSR_SA_HEALTH_STATE = "Error event on subscribing Subarray HealthState!\n"
ERR_CONFIGURE_CMD = "Exception in Configure command: \n "

ENUM_OK, ENUM_DEGRADED, ENUM_FAILED, ENUM_UNKNOWN = range(0, 4)
