# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
A Leaf control node for DishMaster.
"""

import tango
from tango import DevFailed

from ska.base.commands import  BaseCommand
from tmc.common.tango_client import TangoClient
from .command_callback import CommandCallBack


class SetStandbyFPMode(BaseCommand):
    """
    A class for DishLeafNode's SetStandbyFPMode() command.
    """

    def do(self):
        """
        Invokes SetStandbyFPMode command on DishMaster (Standby-Full power) mode.

        :raises DevFailed: If error occurs while invoking SetStandbyFPMode command on DishMaster.
        """
        device_data = self.target
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb


        command_name = "SetStandbyFPMode"
        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            dish_client.send_command_async(command_name, None, cmd_ended_cb)
            #device._dish_proxy.command_inout_asynch(command_name, device.cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = f"Exception occured while executing the '{command_name}' command."
            device_data._read_activity_message = log_message
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                "SetStandbyFPMode.do()",
                tango.ErrSeverity.ERR,
            )

