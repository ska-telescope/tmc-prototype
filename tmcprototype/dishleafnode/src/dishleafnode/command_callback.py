# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
CommandCallBack class for DishLeafNode.
"""
from tmc.common.tango_server_helper import TangoServerHelper


class CommandCallBack:
    def __init__(self, log):
        self.logger = log

    def cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the command has been successfully invoked on DishMaster.

        :param event: a CmdDoneEvent object. This object is used to pass data
            to the callback method in asynchronous callback model for command
            execution.
        :type: CmdDoneEvent object
            It has the following members:
            - cmd_name   : (str) The command name
            - argout_raw : (DeviceData) The command argout
            - argout     : The command argout
            - err        : (bool) A boolean flag set to True if the command failed.
                            False otherwise
            - errors     : (sequence<DevError>) The error stack
            - ext
        """
        this_server = TangoServerHelper.get_instance()
        if event.err:
            log_message = f"Error in invoking command: {event.cmd_name}\n{event.errors}"
            self.logger.error(log_message)
            this_server.write_attr("activityMessage", log_message, False)
        else:
            log_message = f"Command :-> {event.cmd_name} invoked successfully."
            self.logger.info(log_message)
            this_server.write_attr("activityMessage", log_message, False)
