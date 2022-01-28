import json
import time
from os.path import dirname, join

import mock
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.configure_command import Configure
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm_parametrize, logger

SDP_SUBARRAY_DEVICE = "mid_sdp/elt/subarray_1"


def get_configure_input_str(configure_input_file="command_Configure.json"):
    path = join(dirname(__file__), "..", "..", "data", configure_input_file)
    with open(path, "r") as f:
        configure_input_file = f.read()
    return configure_input_file


def get_configure_command_obj():
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_1"

    cm.update_device_obs_state(dev_name, ObsState.READY)
    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    configure_command = Configure(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    cm.get_device(dev_name).obsState == ObsState.READY

    return configure_command, my_adapter_factory


def test_telescope_configure_command(tango_context):
    logger.info("%s", tango_context)
    configure_command, my_adapter_factory = get_configure_command_obj()

    configure_input_str = get_configure_input_str()
    assert configure_command.check_allowed()
    (result_code, _) = configure_command.do(configure_input_str)
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Configure.assert_called()


def test_telescope_configure_resources_command_missing_interface_key(
    tango_context,
):
    logger.info("%s", tango_context)
    configure_command, my_adapter_factory = get_configure_command_obj()

    configure_input_str = get_configure_input_str()
    json_argument = json.loads(configure_input_str)
    json_argument["interface"] = ""
    assert configure_command.check_allowed()
    (result_code, _) = configure_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Configure.assert_called()


def test_telescope_configure_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    failing_dev = "mid_sdp/elt/subarray_1"
    attrs = {"Configure.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    configure_command = Configure(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    cm.update_device_obs_state(failing_dev, ObsState.READY)
    configure_input_str = get_configure_input_str()
    assert configure_command.check_allowed()
    (result_code, message) = configure_command.do(configure_input_str)
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_configure_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    configure_command, _ = get_configure_command_obj()
    assert configure_command.check_allowed()
    (result_code, _) = configure_command.do("")
    assert result_code == ResultCode.FAILED


def test_telescope_configure_command_missing_scan_type(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    configure_command, _ = get_configure_command_obj()

    configure_input_str = get_configure_input_str()
    json_argument = json.loads(configure_input_str)
    del json_argument["scan_type"]
    assert configure_command.check_allowed()
    (result_code, message) = configure_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.FAILED
    assert "scan_type" in message
