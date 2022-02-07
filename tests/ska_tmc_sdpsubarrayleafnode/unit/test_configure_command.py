import json
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from ska_tmc_sdpsubarrayleafnode.commands.configure_command import Configure
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


def get_configure_input_str(configure_input_file="command_Configure.json"):
    path = join(dirname(__file__), "..", "..", "data", configure_input_file)
    with open(path, "r") as f:
        configure_input_file = f.read()
    return configure_input_file


@pytest.mark.sdpsln
def test_telescope_configure_command(tango_context):
    logger.info("%s", tango_context)
    _, configure_command, my_adapter_factory = get_sdpsln_command_obj(
        Configure, obsstate_value=ObsState.READY
    )
    configure_input_str = get_configure_input_str()
    assert configure_command.check_allowed()
    (result_code, _) = configure_command.do(configure_input_str)
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.Configure.assert_called()


@pytest.mark.sdpsln
def test_telescope_configure_resources_command_missing_interface_key(
    tango_context,
):
    logger.info("%s", tango_context)
    _, configure_command, my_adapter_factory = get_sdpsln_command_obj(
        Configure, obsstate_value=ObsState.READY
    )

    configure_input_str = get_configure_input_str()
    json_argument = json.loads(configure_input_str)
    json_argument["interface"] = ""
    assert configure_command.check_allowed()
    (result_code, _) = configure_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.Configure.assert_called()


@pytest.mark.sdpsln
def test_telescope_configure_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    attrs = {"Configure.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, proxy=subarrayMock
    )

    configure_command = Configure(
        cm, cm.op_state_model, adapter_factory, skuid
    )
    cm.update_device_obs_state(ObsState.READY)
    configure_input_str = get_configure_input_str()
    assert configure_command.check_allowed()
    (result_code, message) = configure_command.do(configure_input_str)
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.sdpsln
def test_telescope_configure_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    _, configure_command, _ = get_sdpsln_command_obj(
        Configure, obsstate_value=ObsState.READY
    )
    assert configure_command.check_allowed()
    (result_code, _) = configure_command.do("")
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsln
def test_telescope_configure_command_missing_scan_type(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    _, configure_command, _ = get_sdpsln_command_obj(
        Configure, obsstate_value=ObsState.READY
    )

    configure_input_str = get_configure_input_str()
    json_argument = json.loads(configure_input_str)
    del json_argument["scan_type"]
    assert configure_command.check_allowed()
    (result_code, message) = configure_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.FAILED
    assert "scan_type" in message
