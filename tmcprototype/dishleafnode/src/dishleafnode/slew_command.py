# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.


"""
Slew class for DishLeafNode.
"""

import tango
from tango import DevFailed, DevState

from ska.base.commands import  BaseCommand
from tmc.common.tango_client import TangoClient
from .command_callback import CommandCallBack

class Slew(BaseCommand):
    """
    A class for DishLeafNode's SlewCommand() command.

    Invokes Slew command on DishMaster to slew the dish towards the set pointing
    coordinates.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean
        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            return False

        return True

    def do(self, argin):
        """
        Method to invoke Slew command on Dish Master.

        :param argin: list
            [0] = Azimuth, in degrees
            [1] = Elevation, in degrees

        raises:
            DevFailed If error occurs while invoking Slew command on DishMaster.

        """
        device_data = self.target
        command_name = "Slew"
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            dish_client.send_command_async(command_name, command_data=argin, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = f"Exception occured while executing the '{command_name}' command."
            device_data._read_activity_message = log_message
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                "Slew.do()",
                tango.ErrSeverity.ERR,
            )

