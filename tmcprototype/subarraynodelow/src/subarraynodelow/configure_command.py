"""
ConfigureCommand class for SubarrayNodeLow.
"""

import json
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from ska_telmodel.csp import interface

csp_interface_version = 0
sdp_interface_version = 0


class ConfigureCommand(SKASubarray.ConfigureCommand):
    """
    A class for SubarrayNodeLow's Configure() command.
    """

    def do(self, argin):
        """
        Configures the resources assigned to the Mccs Subarray.
    
        :param argin: DevString.

        JSON string example is:
                {
            "stations": [
                {
                "station_id": 1,
                "tile_ids": [
                    1,
                    2
                ]
                },
                {
                "station_id": 2,
                "tile_ids": [
                    3,
                    4
                ]
                }
            ],
            "station_beam_pointings": [
                {
                "station_beam_id": 1,
                "target": {
                    "system": "HORIZON",
                    "name": "DriftScan",
                    "Az": 180.0,
                    "El": 45.0
                },
                "update_rate": 0.0,
                "channels": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8
                ]
                }
            ]
            }
        :return: A tuple containing a return code and a string message indicating status.
         The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: JSONDecodeError if input argument json string contains invalid value
        """
        device = self.target
        device.is_scan_completed = False
        device.is_release_resources = False
        self.logger.info(const.STR_CONFIGURE_CMD_INVOKED_SA_LOW)
        log_msg = const.STR_CONFIGURE_IP_ARG + str(argin)
        self.logger.info(log_msg)
        device.set_status(const.STR_CONFIGURE_CMD_INVOKED_SA_LOW)
        device._read_activity_message = const.STR_CONFIGURE_CMD_INVOKED_SA_LOW
        # try:
        #     scan_configuration = json.loads(argin)
        # except json.JSONDecodeError as jerror:
        #     log_message = const.ERR_INVALID_JSON + str(jerror)
        #     self.logger.error(log_message)
        #     device._read_activity_message = log_message
        #     tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
        #                                  const.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)
        # tmc_configure = scan_configuration["tmc"]
        # device.scan_duration = int(tmc_configure["scanDuration"])
        # # self._configure_dsh(scan_configuration)
        # # self._configure_csp(scan_configuration)
        # # self._configure_sdp(scan_configuration)
        try:
            device._mccs_subarray_ln_proxy.command_inout(const.CMD_CONFIGURE, argin)
            message = "Configure command invoked"
            self.logger.info(message)
            return (ResultCode.STARTED, message)
        except DevFailed as df:
            log_message = df[0].desc
            device._read_activity_message = log_message
            #log_msg = "Failed to configure %s. %s" % (device_proxy.dev_name(), df)
            self.logger.error(log_msg)
            raise

    # def _configure_leaf_node(self, device_proxy, cmd_name, cmd_data):
    #     device = self.target
    #     try:
    #         device_proxy.command_inout(cmd_name, cmd_data)
    #         log_msg = "%s configured succesfully." % device_proxy.dev_name()
    #         self.logger.debug(log_msg)
    #     except DevFailed as df:
    #         log_message = df[0].desc
    #         device._read_activity_message = log_message
    #         log_msg = "Failed to configure %s. %s" % (device_proxy.dev_name(), df)
    #         self.logger.error(log_msg)
    #         raise

    # def _create_cmd_data(self, method_name, scan_config, *args):
    #     device = self.target
    #     try:
    #         method = getattr(ElementDeviceData, method_name)
    #         cmd_data = method(scan_config, *args)
    #     except KeyError as kerr:
    #         log_message = kerr.args[0]
    #         device._read_activity_message = log_message
    #         self.logger.debug(log_message)
    #         raise
    #     return cmd_data

    # def _configure_mccs_subarray_leaf_node(self, scan_configuration):
    #     device = self.target
    #     cmd_data = self._create_cmd_data(scan_config, scan_configuration)
    #     self._configure_leaf_node(device._mccs_sa_proxy, "Configure", cmd_data)



    # def _configure_sdp(self, scan_configuration):
    #     device = self.target
    #     cmd_data = self._create_cmd_data("build_up_sdp_cmd_data", scan_configuration)
    #     self._configure_leaf_node(device._sdp_subarray_ln_proxy, "Configure", cmd_data)

    # def _configure_csp(self, scan_configuration):
    #     device = self.target
    #     attr_name_map = {
    #         const.STR_DELAY_MODEL_SUB_POINT: device.CspSubarrayLNFQDN + "/delayModel",
    #     }
    #     cmd_data = self._create_cmd_data(
    #         "build_up_csp_cmd_data", scan_configuration, attr_name_map, device._receive_addresses_map)
    #     self._configure_leaf_node(device._csp_subarray_ln_proxy, "Configure", cmd_data)

    # def _configure_dsh(self, scan_configuration):
    #     device = self.target
    #     config_keys = scan_configuration.keys()
    #     if not set(["sdp", "csp"]).issubset(config_keys) and "dish" in config_keys:
    #         device.only_dishconfig_flag = True

    #     cmd_data = self._create_cmd_data(
    #         "build_up_dsh_cmd_data", scan_configuration, device.only_dishconfig_flag)

        # try:
        #     device._dish_leaf_node_group.command_inout(const.CMD_CONFIGURE, cmd_data)
        #     self.logger.info("Configure command is invoked on the Dish Leaf Nodes Group")
        #     device._dish_leaf_node_group.command_inout(const.CMD_TRACK, cmd_data)
        #     self.logger.info('TRACK command is invoked on the Dish Leaf Node Group')
        # except DevFailed as df:
        #     device._read_activity_message = df[0].desc
        #     self.logger.error(df)
        #     raise


