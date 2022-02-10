import json
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.assign_resources_command import (
    AssignResources,
)
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


def get_assign_input_str(assign_input_file="command_AssignResources.json"):
    path = join(dirname(__file__), "..", "..", "data", assign_input_file)
    with open(path, "r") as f:
        assign_input_str = f.read()
    return assign_input_str


@pytest.mark.sdpsln
def test_telescope_assign_resources_command(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, my_adapter_factory = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )

    assign_input_str = get_assign_input_str()
    assert assign_res_command.check_allowed()
    (result_code, _) = assign_res_command.do(assign_input_str)
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.AssignResources.assert_called()


@pytest.mark.sdpsln
def test_telescope_assign_resources_command_missing_eb_id_key(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, my_adapter_factory = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )
    assign_input_str = get_assign_input_str()
    json_argument = json.loads(assign_input_str)
    json_argument["eb_id"] = ""
    assert assign_res_command.check_allowed()
    (result_code, _) = assign_res_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.AssignResources.assert_called()


@pytest.mark.sdpsln
def test_telescope_assign_resources_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    attrs = {"AssignResources.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, proxy=subarrayMock
    )

    assign_res_command = AssignResources(
        cm, cm.op_state_model, adapter_factory, skuid
    )
    assign_input_str = get_assign_input_str()
    assert assign_res_command.check_allowed()
    (result_code, message) = assign_res_command.do(assign_input_str)
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.sdpsln
def test_telescope_assign_resources_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )
    assert assign_res_command.check_allowed()
    (result_code, _) = assign_res_command.do("")
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsln
def test_telescope_assign_resources_command_missing_scan_types(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )
    scan_types_key = "scan_types"
    assign_input_str = get_assign_input_str()
    json_argument = json.loads(assign_input_str)
    del json_argument[scan_types_key]
    assert assign_res_command.check_allowed()
    (result_code, message) = assign_res_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.FAILED
    assert scan_types_key in message
