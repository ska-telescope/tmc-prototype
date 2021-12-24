# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.


"""
EndScan class for DishLeafNode.
"""
# Tango imports
import tango

# Additional import
from ska.base.commands import BaseCommand
from tango import DevFailed, DevState
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from .command_callback import CommandCallBack


class EndScan(BaseCommand):
    """
    A class for DishLeafNode's EndScan() command.
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
        Invokes Endscan command on DishMaster.

        param argin:
            timestamp

        raises:
            DevFailed If error occurs while invoking StopCapture command on DishMaster.

        """
        command_name = "EndScan"
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

        try:
            this_server = TangoServerHelper.get_instance()
            self.dish_master_fqdn = ""
            property_value = this_server.read_property("DishMasterFQDN")
            self.dish_master_fqdn = self.dish_master_fqdn.join(property_value)
            dish_client = TangoClient(self.dish_master_fqdn)
            dish_client.send_command_async(
                "StopCapture", callback_method=cmd_ended_cb
            )
            self.logger.info(
                "'%s' command executed successfully.", command_name
            )
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = f"Exception occured while executing the '{command_name}' command."
            this_server.write_attr("activityMessage", log_message, False)
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                "EndScan.do()",
                tango.ErrSeverity.ERR,
            )
