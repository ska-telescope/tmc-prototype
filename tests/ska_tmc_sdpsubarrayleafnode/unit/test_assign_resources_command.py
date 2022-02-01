import json
import time
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.assign_resources_command import (
    AssignResources,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
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


@pytest.mark.sdpsaln
def test_telescope_assign_resources_command(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, my_adapter_factory = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )

    assign_input_str = get_assign_input_str()
    assert assign_res_command.check_allowed()
    (result_code, _) = assign_res_command.do(assign_input_str)
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.AssignResources.assert_called()


@pytest.mark.sdpsaln
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
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.AssignResources.assert_called()


@pytest.mark.sdpsaln
def test_telescope_assign_resources_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm(
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
    attrs = {"AssignResources.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    assign_res_command = AssignResources(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    assign_input_str = get_assign_input_str()
    assert assign_res_command.check_allowed()
    (result_code, message) = assign_res_command.do(assign_input_str)
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpsaln
def test_telescope_assign_resources_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )
    assert assign_res_command.check_allowed()
    (result_code, _) = assign_res_command.do("")
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsaln
def test_telescope_assign_resources_command_missing_scan_types(tango_context):
    logger.info("%s", tango_context)
    _, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, ObsState.IDLE
    )
    assign_input_str = get_assign_input_str()
    json_argument = json.loads(assign_input_str)
    del json_argument["scan_types"]
    assert assign_res_command.check_allowed()
    (result_code, message) = assign_res_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.FAILED
    assert "scan_types" in message