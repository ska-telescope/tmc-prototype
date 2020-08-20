"""
ConfigureCommand class for SubarrayNode.
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
    A class for SubarrayNode's Configure() command.
    """

    def do(self, argin):
        """
        Configures the resources assigned to the Subarray.The configuration data for SDP, CSP and Dish is
        extracted out of the input configuration string and relayed to the respective underlying devices (SDP
        Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node).

        :param argin: DevString.

        JSON string that includes pointing parameters of Dish - Azimuth and Elevation Angle, CSP
        Configuration and SDP Configuration parameters.
        JSON string example is:
        {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
        "dish":{"receiverBand":"1"},"csp":{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1",
        "fsp":[{"fspID":1,"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0}]},
        "sdp":{"scan_type":"science_A"},"tmc":{"scanDuration":10.0}}
        CSP block in json string is as per earlier implementation and not aligned to SP-872
        Note: While invoking this command from JIVE, provide above JSON string without any space.

        :return: A tuple containing a return code and a string message indicating status.
         The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: JSONDecodeError if input argument json string contains invalid value
        """
        device = self.target
        device.is_scan_completed = False
        device.is_release_resources = False
        device.is_restart_command = False
        device.is_abort_command = False
        self.logger.info(const.STR_CONFIGURE_CMD_INVOKED_SA)
        log_msg = const.STR_CONFIGURE_IP_ARG + str(argin)
        self.logger.info(log_msg)
        device.set_status(const.STR_CONFIGURE_CMD_INVOKED_SA)
        device._read_activity_message = const.STR_CONFIGURE_CMD_INVOKED_SA
        try:
            scan_configuration = json.loads(argin)
        except json.JSONDecodeError as jerror:
            log_message = const.ERR_INVALID_JSON + str(jerror)
            self.logger.error(log_message)
            device._read_activity_message = log_message
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_message,
                                         const.STR_CONFIGURE_EXEC, tango.ErrSeverity.ERR)
        tmc_configure = scan_configuration["tmc"]
        device.scan_duration = int(tmc_configure["scanDuration"])
        self._configure_dsh(scan_configuration)
        self._configure_csp(scan_configuration)
        self._configure_sdp(scan_configuration)
        message = "Configure command invoked"
        self.logger.info(message)
        return (ResultCode.STARTED, message)

    def _configure_leaf_node(self, device_proxy, cmd_name, cmd_data):
        device = self.target
        try:
            device_proxy.command_inout(cmd_name, cmd_data)
            log_msg = "%s configured succesfully." % device_proxy.dev_name()
            self.logger.debug(log_msg)
        except DevFailed as df:
            log_message = df[0].desc
            device._read_activity_message = log_message
            log_msg = "Failed to configure %s. %s" % (device_proxy.dev_name(), df)
            self.logger.error(log_msg)
            raise

    def _create_cmd_data(self, method_name, scan_config, *args):
        device = self.target
        try:
            method = getattr(ElementDeviceData, method_name)
            cmd_data = method(scan_config, *args)
        except KeyError as kerr:
            log_message = kerr.args[0]
            device._read_activity_message = log_message
            self.logger.debug(log_message)
            raise
        return cmd_data

    def _configure_sdp(self, scan_configuration):
        device = self.target
        cmd_data = self._create_cmd_data("build_up_sdp_cmd_data", scan_configuration)
        self._configure_leaf_node(device._sdp_subarray_ln_proxy, "Configure", cmd_data)

    def _configure_csp(self, scan_configuration):
        device = self.target
        attr_name_map = {
            const.STR_DELAY_MODEL_SUB_POINT: device.CspSubarrayLNFQDN + "/delayModel",
        }
        cmd_data = self._create_cmd_data(
            "build_up_csp_cmd_data", scan_configuration, attr_name_map, device._receive_addresses_map)
        self._configure_leaf_node(device._csp_subarray_ln_proxy, "Configure", cmd_data)

    def _configure_dsh(self, scan_configuration):
        device = self.target
        config_keys = scan_configuration.keys()
        if not set(["sdp", "csp"]).issubset(config_keys) and "dish" in config_keys:
            device.only_dishconfig_flag = True

        cmd_data = self._create_cmd_data(
            "build_up_dsh_cmd_data", scan_configuration, device.only_dishconfig_flag)

        try:
            device._dish_leaf_node_group.command_inout(const.CMD_CONFIGURE, cmd_data)
            self.logger.info("Configure command is invoked on the Dish Leaf Nodes Group")
            device._dish_leaf_node_group.command_inout(const.CMD_TRACK, cmd_data)
            self.logger.info('TRACK command is invoked on the Dish Leaf Node Group')
        except DevFailed as df:
            device._read_activity_message = df[0].desc
            self.logger.error(df)
            raise


class ElementDeviceData:
    @staticmethod
    def build_up_sdp_cmd_data(scan_config):
        scan_config = scan_config.copy()
        sdp_scan_config = scan_config.get("sdp", {})
        if sdp_scan_config:
            scan_type = sdp_scan_config.get("scan_type")
            if not scan_type:
                raise KeyError("SDP Subarray scan_type is empty. Command data not built up")
        else:
            # Need to check if sdp already has scan type if yes then msg showing continue with old scan .
            # and if no earlier scan exist throw error as below.
            raise KeyError("SDP configuration must be given. Aborting SDP configuration.")
        return json.dumps(sdp_scan_config)

    @staticmethod
    def build_up_csp_cmd_data(scan_config, attr_name_map, receive_addresses_map):
        '''
        Here the input data for CSP is build which is used in configuration of CSP.
        Below is the csp_config_schema variable value generated by using ska_telmodel library.
        {'id': 'sbi-mvp01-20200325-00001-science_A', 'frequencyBand': '1', 'fsp': [{'fspID': 1, 'functionMode'
        : 'CORR', 'frequencySliceID': 1, 'integrationTime': 1400, 'corrBandwidth': 0, 'channelAveragingMap':
        [[0, 2], [744, 0]], 'fspChannelOffset': 0, 'outputLinkMap': [[0, 0], [200, 1]], 'outputHost':
        [[0, '192.168.0.1'], [400, '192.168.0.2']], 'outputMac': [[0, '06-00-00-00-00-00']], 'outputPort':
        [[0, 9000, 1], [400, 9000, 1]]}, {'fspID': 2, 'functionMode': 'CORR', 'frequencySliceID': 2,
        'integrationTime': 1400, 'corrBandwidth': 0, 'channelAveragingMap': [[0, 2], [744, 0]],
        'fspChannelOffset': 744, 'outputLinkMap': [[0, 4], [200, 5]], 'outputHost': [[0, '192.168.0.3'],
        [400, '192.168.0.4']], 'outputMac': [[0, '06-00-00-00-00-01']], 'outputPort': [[0, 9000, 1],
        [400, 9000, 1]]}]}

        :return: csp confiuration schema
        '''
        scan_config = scan_config.copy()
        csp_scan_config = scan_config.get("csp", {})
        if csp_scan_config:
            scan_type = scan_config["sdp"]["scan_type"]
            if scan_type:
                # Invoke ska_telmodel library function to create csp configure schema
                if receive_addresses_map:
                    csp_config_schema = interface.make_csp_config(csp_interface_version, sdp_interface_version,
                                        scan_type, csp_scan_config, receive_addresses_map)
                    csp_config_schema = json.loads(csp_config_schema)
                else:
                    raise KeyError("Receive addresses must be given. Aborting CSP configuration.")
            else:
                raise KeyError("SDP Subarray scan_type is empty")

            if csp_config_schema:
                for key, attribute_name in attr_name_map.items():
                    csp_config_schema[key] = attribute_name
                csp_config_schema["pointing"] = scan_config["pointing"]
            else:
                raise KeyError("CSP configuration schema must be given. Aborting CSP configuration.")

        else:
            raise KeyError("CSP configuration must be given. Aborting CSP configuration.")
        return json.dumps(csp_config_schema)

    @staticmethod
    def build_up_dsh_cmd_data(scan_config, only_dishconfig_flag):
        scan_config = scan_config.copy()
        if set(["pointing", "dish"]).issubset(scan_config.keys()) or only_dishconfig_flag:
            scan_config.pop("sdp", None)
            scan_config.pop("csp", None)
            scan_config.pop("tmc", None)
            cmd_data = tango.DeviceData()
            cmd_data.insert(tango.DevString, json.dumps(scan_config))
        else:
            raise KeyError("Dish configuration must be given. Aborting Dish configuration.")
        return cmd_data