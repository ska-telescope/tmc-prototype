# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
Configure class for DishLeafNode.
"""
# Standard Python imports

# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from .command_callback import CommandCallBack


class Configure(BaseCommand):
    """
    A class for DishLeafNode's Configure() command.

    Configures the Dish by setting pointing coordinates for a given scan.
    This function accepts the input json and calculate pointing parameters of Dish- Azimuth
    and Elevation Angle. Calculated parameters are again converted to json and fed to the
    dish master.

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
            DevState.INIT,
        ]:
            return False

        return True

    def do(self, argin):
        """
        Method to invoke Configure command on dish.

        :param argin:
            A String in a JSON format that includes pointing parameters of Dish- Azimuth and
            Elevation Angle.

                Example:
                {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
                "dish":{"receiverBand":"1"}}

        return:
            None

        raises:
            DevFailed If error occurs while invoking ConfigureBand<> command on DishMaster or
            if the json string contains invalid data.

        """

        device_data = self.target
        command_name = "Configure"

        try:
            this_server = TangoServerHelper.get_instance()
            self.dish_master_fqdn = ""
            property_value = this_server.read_property("DishMasterFQDN")
            self.dish_master_fqdn = self.dish_master_fqdn.join(property_value)
            json_argument = device_data._load_config_string(argin)
            receiver_band = json_argument["dish"]["receiverBand"]
            self._configure_band(receiver_band)
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
                f"DishLeafNode.{command_name}Command",
                tango.ErrSeverity.ERR,
            )

        self.logger.info("'%s' command executed successfully.", command_name)

    def _configure_band(self, band):
        """"Send the ConfigureBand<band-number> command to Dish Master"""
        command_name = f"ConfigureBand{band}"

        try:
            dish_client = TangoClient(self.dish_master_fqdn)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
        except DevFailed as dev_failed:
            raise dev_failed

    # pylint: enable= unbalanced-tuple-unpacking
