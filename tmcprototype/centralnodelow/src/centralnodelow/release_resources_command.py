class ReleaseResources(BaseCommand):
    """
    A class for CentralNode's ReleaseResources() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """

        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE, ]:
            tango.Except.throw_exception("Command ReleaseResources is not allowed in current state.",
                                         "Failed to invoke ReleaseResources command on CentralNode.",
                                         "CentralNode.ReleaseResources()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self, argin):
        """
        Release all the resources assigned to the given Subarray. It accepts the subarray id, release_all flag in JSON string format. When the release_all flag is True, ReleaseAllResources command
        is invoked on the respective SubarrayNode.

        :param argin: The string in JSON format. The JSON contains following values:

            subarray_id:
                DevShort. Mandatory.

            release_all:
                Boolean(True or False). Mandatory. True when all the resources to be released from Subarray.

            Example:
                {
                    "subarray_id": 1,
                    "release_all": true,
                }

            Note: From Jive, enter input as:
                {"subarray_id":1,"release_all":true} without any space.

         :raises: ValueError if input argument json string contains invalid value
                KeyError if input argument json string contains invalid key
                DevFailed if the command execution or command invocation on SubarrayNode is not successful

        """
        device = self.target
        try:
            jsonArgument = json.loads(argin)
            subarray_id = jsonArgument['subarray_id']
            subarrayProxy = device.subarray_FQDN_dict[subarray_id]
            if jsonArgument['release_all'] == True:
                # Invoke ReleaseAllResources on SubarrayNode
                subarrayProxy.command_inout(const.CMD_RELEASE_RESOURCES)
                # Invoke ReleaseAllResources on MCCS Master Leaf Node
                # Send same input argument to MCCS Master for ReleaseResource Command
                device._mccs_master_leaf_proxy.command_inout(const.CMD_RELEASE_MCCS_RESOURCES, argin)
                log_msg = const.STR_REL_RESOURCES
                self.logger.info(log_msg)
                device._read_activity_message = log_msg
            else:
                device._read_activity_message = const.STR_FALSE_TAG
                self.logger.info(const.STR_FALSE_TAG)

        except ValueError as value_error:
            self.logger.error(const.ERR_INVALID_JSON)
            device._read_activity_message = const.ERR_INVALID_JSON + str(value_error)
            log_msg = const.ERR_INVALID_JSON + str(value_error)
            self.logger.exception(value_error)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                         "CentralNode.ReleaseResourcesCommand",
                                         tango.ErrSeverity.ERR)

        except KeyError as key_error:
            self.logger.error(const.ERR_JSON_KEY_NOT_FOUND)
            device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.exception(key_error)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                         "CentralNode.ReleaseResourcesCommand",
                                         tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RELEASE_RESOURCES + str(dev_failed)
            device._read_activity_message = const.ERR_RELEASE_RESOURCES
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                         "CentralNode.ReleaseResourcesCommand",
                                         tango.ErrSeverity.ERR)
