"""
AssignResourcesCommand class for SubarrayNode.
"""

from concurrent.futures import ThreadPoolExecutor
import json
# Tango imports
import tango
from tango import DevFailed
# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class AssignResourcesCommand(SKASubarray.AssignResourcesCommand):
    """
    A class for SubarrayNode's AssignResources() command.
    """
    def do(self, argin):
        """
        Assigns resources to the subarray. It accepts receptor id list as well as SDP resources string
        as a DevString. Upon successful execution, the 'receptorIDList' attribute of the
        subarray is updated with the list of receptors and SDP resources string is pass to SDPSubarrayLeafNode,
        and returns list of assigned resources as well as passed SDP string as a DevString.

        Note: Resource allocation for CSP and SDP resources is also implemented but
        currently CSP accepts only receptorIDList and SDP accepts resources allocated to it.

        :param argin: DevString.

        Example:

        {"dish":{"receptorIDList":["0002","0001"]},"sdp":{"id":
        "sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A",
        "coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","channels":
        [{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,
        "link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,
        "freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]},{"id":
        "calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
        "channels":[{"count":744,"start":0,"stride":2,"freq_min":0.35e9,
        "freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,
        "start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],
        [2200,5]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":
        {"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters":{}},
        {"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_realtime",
        "version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":
        {"type":"batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":[
        {"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"]}]},{"id":
        "pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":"0.1.0"},
        "parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":
        ["calibration"]}]}]}}


        :return: A tuple containing a return code and string of Resources added to the Subarray.
            Example of string of Resources :
                ["0001","0002"]
            as argout if allocation successful.

        :rtype: (ResultCode, str)

        :raises: ValueError if input argument json string contains invalid value
                DevFailed if the command execution is not successful

        """

        # exception_count = 0
        # exception_message = []
        device = self.target
        argout = []
        device.is_end_command = False
        device.is_release_resources = False
        device.is_restart_command = False
        device.is_abort_command = False
        # Validate if Subarray is in IDLE obsState
        # TODO: Need to get idea if this is required?
        # try:
        #     self.validate_obs_state()
        # except InvalidObsStateError as error:
        #     self.logger.exception(error)
        #     tango.Except.throw_exception("Subarray is not in IDLE obsState",
        #                     "SubarrayNode raised InvalidObsStateError in AssignResources command",
        #                     "subarraynode.AssignResources()", tango.ErrSeverity.ERR)

        # 1. Argument validation
        try:
            # Allocation success and failure lists
            resources = json.loads(argin)
            receptor_list = resources["dish"]["receptorIDList"]
            sdp_resources = resources.get("sdp")
            device._sb_id = resources["sdp"]["id"]

            for leafId in range(0, len(receptor_list)):
                float(receptor_list[leafId])
            # validation of SDP and CSP resources yet to be implemented as of now reources are not present.
        except json.JSONDecodeError as json_error:
            self.logger.exception(const.ERR_INVALID_JSON)
            message = const.ERR_INVALID_JSON + str(json_error)
            device._read_activity_message = message
            tango.Except.throw_exception(const.STR_CMD_FAILED, message,
                                         const.STR_ASSIGN_RES_EXEC, tango.ErrSeverity.ERR)
        except ValueError as value_error:
            self.logger.exception(const.ERR_INVALID_DATATYPE)
            message = const.ERR_INVALID_DATATYPE + value_error
            device._read_activity_message = message
            tango.Except.throw_exception(const.STR_CMD_FAILED, message,
                                         const.STR_ASSIGN_RES_EXEC, tango.ErrSeverity.ERR)

        with ThreadPoolExecutor(3) as executor:
            # 2.1 Create group of receptors
            self.logger.debug(const.STR_DISH_ALLOCATION)
            dish_allocation_status = executor.submit(self.add_receptors_in_group, receptor_list)

            # 2.2. Add resources in CSP subarray
            self.logger.debug(const.STR_CSP_ALLOCATION)
            csp_allocation_status = executor.submit(self.assign_csp_resources, receptor_list)

            # 2.3. Add resources in SDP subarray
            self.logger.debug(const.STR_SDP_ALLOCATION)
            sdp_allocation_status = executor.submit(self.assign_sdp_resources, sdp_resources)

            # 2.4 wait for result
            while (dish_allocation_status.done() is False or
                   csp_allocation_status.done() is False or
                   sdp_allocation_status.done() is False
            ):
                pass

            # 2.5. check results
            try:
                dish_allocation_result = dish_allocation_status.result()
                log_msg = const.STR_DISH_ALLOCATION_RESULT + str(dish_allocation_result)
                self.logger.debug(log_msg)
                dish_allocation_result.sort()
                self.logger.debug("Dish group is created successfully")
            except DevFailed as df:
                self.logger.exception("Dish allocation failed.")
                tango.Except.re_throw_exception(
                    df,
                    "Dish allocation failed.",
                    "Failed to allocate receptors to Subarray.",
                    "SubarrayNode.AssignResources",
                    tango.ErrSeverity.ERR
                )

            try:
                csp_allocation_result = csp_allocation_status.result()
                log_msg = const.STR_CSP_ALLOCATION_RESULT + str(csp_allocation_result)
                self.logger.debug(log_msg)

                csp_allocation_result.sort()
                # assert csp_allocation_result == receptor_list
                self.logger.info("Assign Resources on CSPSubarray successful")
            except DevFailed as df:
                # The exception is already logged so not logged again.
                tango.Except.re_throw_exception(
                    df,
                    "CSP allocation failed.",
                    "Failed to allocate CSP resources to Subarray.",
                    "SubarrayNode.AssignResources",
                    tango.ErrSeverity.ERR
                )

            try:
                sdp_allocation_result = sdp_allocation_status.result()
                log_msg = const.STR_SDP_ALLOCATION_RESULT + str(sdp_allocation_result)
                self.logger.debug(log_msg)
                self.logger.info("Assign Resources on SDPSubarray successful")
            except DevFailed as df:
                # The exception is already logged so not logged again.
                tango.Except.re_throw_exception(df,
                    "SDP allocation failed.",
                    "Failed to allocate SDP resources to Subarray.",
                    "SubarrayNode.AssignResources",
                    tango.ErrSeverity.ERR
                )

            # TODO: For future use
            # sdp_allocation_result = sdp_allocation_status.result()
            # log_msg = const.STR_SDP_ALLOCATION_RESULT + str(sdp_allocation_result)
            # self.logger.debug(log_msg)

            # try:
            #     assert sdp_allocation_result == sdp_resources
            #     self.logger.info("Assign Resources on SDPSubarray successful")
            # except AssertionError as error:
            #     self.logger.exception("Failed to assign SDP resources: actual %s != %s expected",
            #         sdp_allocation_result, sdp_resources)
            #     tango.Except.throw_exception(
            #         "Assign resources failed on CspSubarrayLeafNode",
            #         str(sdp_allocation_result),
            #         "subarraynode.AssignResources()",
            #         tango.ErrSeverity.ERR)
            # TODO: For future use
            # if(dish_allocation_result == receptor_list and
            #     csp_allocation_result == receptor_list and
            #     sdp_allocation_result == sdp_resources
            #   ):
            #     # Currently sending dish allocation and SDP allocation results.
            #     argout = dish_allocation_result
            # else:
            #     argout = []

        argout = dish_allocation_result
        log_msg = "assign_resource_argout", argout
        self.logger.debug(log_msg)
        message = str(argout)
        return (ResultCode.STARTED, message)

    def add_receptors_in_group(self, argin):
        """
        Creates a tango group of the successfully allocated resources in the subarray.
        Device proxy for each of the resources is created. The healthState and pointintgState attributes
        from all the devices in the group are subscribed so that the changes in the respective device are
        received at Subarray Node.


        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVarStringArray. List of receptor IDs to be allocated to subarray.
            Example: ['0001', '0002']

        :return:
            DevVarStringArray. List of Resources added to the Subarray.
            Example: ['0001', '0002']
        """
        allocation_success = []
        allocation_failure = []
        device = self.target
        # Add each dish into the tango group

        for leafId in range(0, len(argin)):
            try:
                str_leafId = argin[leafId]
                device._dish_leaf_node_group.add(device.DishLeafNodePrefix + str_leafId)
                devProxy = device.get_deviceproxy(device.DishLeafNodePrefix + str_leafId)
                device._dish_leaf_node_proxy.append(devProxy)
                # Update the list allocation_success with the dishes allocated successfully to subarray
                allocation_success.append(str_leafId)
                # Subscribe Dish Health State
                self._event_id = devProxy.subscribe_event(const.EVT_DISH_HEALTH_STATE,
                                                          tango.EventType.CHANGE_EVENT,
                                                          device.health_state_cb,
                                                          stateless=True)
                device._dishLnVsHealthEventID[devProxy] = self._event_id
                device._health_event_id.append(self._event_id)
                log_msg = const.STR_DISH_LN_VS_HEALTH_EVT_ID + str(device._dishLnVsHealthEventID)
                self.logger.debug(log_msg)

                # Subscribe Dish Pointing State
                device.dishPointingStateMap[devProxy] = -1
                self._event_id = devProxy.subscribe_event(const.EVT_DISH_POINTING_STATE,
                                                          tango.EventType.CHANGE_EVENT,
                                                          device.pointing_state_cb,
                                                          stateless=True)
                device._dishLnVsPointingStateEventID[devProxy] = self._event_id
                device._pointing_state_event_id.append(self._event_id)
                log_msg = const.STR_DISH_LN_VS_POINTING_STATE_EVT_ID + str(device._dishLnVsPointingStateEventID)
                self.logger.debug(log_msg)
                device._receptor_id_list.append(int(str_leafId))
                device._read_activity_message = const.STR_GRP_DEF + str(
                    device._dish_leaf_node_group.get_device_list(True))
                device._read_activity_message = const.STR_LN_PROXIES + str(device._dish_leaf_node_proxy)
                self.logger.debug(const.STR_SUBS_ATTRS_LN)
                device._read_activity_message = const.STR_SUBS_ATTRS_LN
                self.logger.info(const.STR_ASSIGN_RES_SUCCESS)
            except DevFailed as dev_failed:
                self.logger.exception("Receptor %s allocation failed.", str_leafId)
                log_msg = const.ERR_ADDING_LEAFNODE + str(dev_failed)
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_ADDING_LEAFNODE,
                                                 log_msg,
                                                 "SubarrayNode.add_receptors_in_group",
                                                 tango.ErrSeverity.ERR
                                                )
                allocation_failure.append(str_leafId)
                # Exception Logic to remove Id from subarray group
                group_dishes = device._dish_leaf_node_group.get_device_list()
                if group_dishes.contains(device.DishLeafNodePrefix + str_leafId):
                    device._dish_leaf_node_group.remove(device.DishLeafNodePrefix + str_leafId)
                # unsubscribe event
                if device._dishLnVsHealthEventID[devProxy]:
                    devProxy.unsubscribe_event(device._dishLnVsHealthEventID[devProxy])

                if device._dishLnVsPointingStateEventID[devProxy]:
                    devProxy.unsubscribe_event(device._dishLnVsPointingStateEventID[devProxy])

            except (TypeError) as except_occurred:
                allocation_failure.append(str_leafId)
                log_msg = const.ERR_ADDING_LEAFNODE + str(except_occurred)
                self.logger.exception(except_occurred)
                tango.Except.throw_exception(const.ERR_ADDING_LEAFNODE, log_msg,
                                             "SubarrayNode.add_receptors_in_group",
                                             tango.ErrSeverity.ERR)

        log_msg = "List of Resources added to the Subarray::",allocation_success
        self.logger.debug(log_msg)
        return allocation_success

    def assign_csp_resources(self, argin):
        """
        This function accepts the receptor IDs list as input and invokes the assign resources command on
        the CSP Subarray Leaf Node.

        :param argin: List of strings
            Contains the list of strings that has the resources ids. Currently this list contains only
            receptor ids.

            Example: ['0001', '0002']

        :return: List of strings.
            Returns the list of CSP resources successfully assigned to the Subarray. Currently, the
            CSPSubarrayLeafNode.AssignResources function returns void. The function only loops back
            the input argument in case of successful resource allocation, or returns exception
            object in case of failure.
        """
        device = self.target
        arg_list = []
        json_argument = {}
        argout = []
        dish = {}
        try:
            dish[const.STR_KEY_RECEPTOR_ID_LIST] = argin
            json_argument[const.STR_KEY_DISH] = dish
            arg_list.append(json.dumps(json_argument))
            device._csp_subarray_ln_proxy.command_inout(const.CMD_ASSIGN_RESOURCES, json.dumps(json_argument))
            self.logger.info(const.STR_ASSIGN_RESOURCES_INV_CSP_SALN)
            argout = argin
        except DevFailed as df:
            # Log exception here as The callstack from this thread wont get
            # propagated to main thread.
            self.logger.exception("CSP Subarray failed to allocate resources.")
            tango.Except.re_throw_exception(df,
                "CSP Subarray failed to allocate resources.",
                "Failed to invoke AssignResources command on CspSubarrayLeafNode.",
                "SubarrayNode.assign_csp_resources",
                tango.ErrSeverity.ERR
            )

        # For this PI CSP Subarray Leaf Node does not return anything. So this function is
        # looping the receptor ids back.
        log_msg = "assign_csp_resources::", argout
        self.logger.debug(log_msg)
        return argout


    def assign_sdp_resources(self, argin):
        """
        This function accepts the receptor ID list as input and assigns SDP resources to SDP Subarray
        through SDP Subarray Leaf Node.

        :param argin: List of strings
            Contains the list of strings that has the resources ids. Currently
            processing block ids are passed to this function.

        :return: List of strings.

            Example: ['PB1', 'PB2']

            Returns the list of successfully assigned resources. Currently the
            SDPSubarrayLeafNode.AssignResources function returns void. Thus, this
            function just loops back the input argument in case of success or returns exception
            object in case of failure.
        """
        device = self.target
        argout = []
        try:
            str_json_arg = json.dumps(argin)
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_ASSIGN_RESOURCES, str_json_arg)
            self.logger.info(const.STR_ASSIGN_RESOURCES_INV_SDP_SALN)
            argout = argin
        except DevFailed as df:
            self.logger.exception("SDP Subarray failed to allocate resources.")
            tango.Except.re_throw_exception(df,
                "SDP Subarray failed to allocate resources.",
                str(df),
                "SubarrayNode.assign_sdp_resources",
                tango.ErrSeverity.ERR
            )

        # For this PI SDP Subarray Leaf Node does not return anything. So this function is
        # looping the processing block ids back.
        log_msg = "assign_sdp_resources::", argout
        self.logger.debug(log_msg)
        return argout
