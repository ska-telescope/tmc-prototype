# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
SetStowMode class for DishLeafNode.
"""

import tango
from tango import DevFailed

from ska.base.commands import  BaseCommand
from tmc.common.tango_client import TangoClient
from .command_callback import CommandCallBack


class SetStowMode(BaseCommand):
    """
    A class for DishLeafNode's SetStowMode() command.
    """

    def do(self):
        """
        Invokes SetStowMode command on DishMaster.

        :param argin: None

        :return: None

        :raises: DevFailed If error occurs while invoking SetStowMode command on DishMaster.
        """
        device_data = self.target
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

        command_name = "SetStowMode"
        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = f"Exception occured while executing the '{command_name}' command."
            device_data._read_activity_message = log_message
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                "SetStowMode.do()",
                tango.ErrSeverity.ERR,
            )

