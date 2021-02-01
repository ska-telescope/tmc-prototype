# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.


"""
Scan class for DishLeafNode.
"""

import tango
from tango import DevFailed, DevState

from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from .command_callback import CommandCallBack


class Scan(BaseCommand):
    """
    A class for DishLeafNode's Scan() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.
        :rtype: boolean
        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            return False

        return True

    def do(self, argin):
        """
        Invokes Scan command on DishMaster.

        :param argin: timestamp
        :raises DevFailed: If error occurs while invoking Scan command on DishMaster.
        """
        device_data = self.target
        command_name = "Scan"
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = (
                f"Exception occured while executing the '{command_name}' command."
            )
            device_data._read_activity_message = log_message
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                "Scan.do()",
                tango.ErrSeverity.ERR,
            )
