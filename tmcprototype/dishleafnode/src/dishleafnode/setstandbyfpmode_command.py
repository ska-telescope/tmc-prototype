# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
SetStandbyFPMode class for DishLeafNode.
"""
# Tango import
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from .command_callback import CommandCallBack


class SetStandbyFPMode(BaseCommand):
    """
    A class for DishLeafNode's SetStandbyFPMode() command.

    Invokes SetStandbyFPMode command on DishMaster (Standby-Full power) mode.

    """

    def do(self):
        """
        Method to Invoke SetStandbyFPMode  on DishMaster.

        param argin:
            None

        return:
            None

        raises:
            DevFailed If error occurs while invoking SetStandbyFPMode command on DishMaster.

        """
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

        command_name = "SetStandbyFPMode"
        try:
            this_server = TangoServerHelper.get_instance()
            self.dish_master_fqdn = ""
            property_value = this_server.read_property("DishMasterFQDN")
            self.dish_master_fqdn = self.dish_master_fqdn.join(property_value)
            dish_client = TangoClient(self.dish_master_fqdn)
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = (
                f"Exception occured while executing the '{command_name}' command."
            )
            this_server.write_attr("activityMessage", log_message, False)
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                "SetStandbyFPMode.do()",
                tango.ErrSeverity.ERR,
            )
