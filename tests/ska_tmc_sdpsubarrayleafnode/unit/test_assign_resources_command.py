import json
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import AssignResources
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
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
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_assign_resources_command(tango_context, devices):
    logger.info("%s", tango_context)
    _, assign_res_command, adapter_factory = get_sdpsln_command_obj(
        AssignResources, devices, ObsState.IDLE
    )

    assign_input_str = get_assign_input_str()
    assert assign_res_command.check_allowed()
    (result_code, msg) = assign_res_command.invoke_assign_resources(
        assign_input_str
    )
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(devices)
    adapter.proxy.command_inout_asynch.assert_called_with(
        "AssignResources",
        json.dumps(json.loads(assign_input_str)),
        assign_res_command.cmd_ended_cb,
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_fail_subarray(tango_context, devices):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    attrs = {"AssignResources.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(devices, proxy=subarrayMock)
    cm.update_device_obs_state(ObsState.EMPTY)
    assign_res_command = AssignResources(
        cm, cm.op_state_model, adapter_factory, skuid
    )
    assign_input_str = get_assign_input_str()
    assert assign_res_command.check_allowed()
    (result_code, message) = assign_res_command.invoke_assign_resources(
        assign_input_str
    )
    assert result_code == ResultCode.FAILED
    assert devices in message


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_empty_input_json(tango_context, devices):
    logger.info("%s", tango_context)
    _, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, devices, ObsState.IDLE
    )
    assert assign_res_command.check_allowed()
    (result_code, _) = assign_res_command.invoke_assign_resources("")
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_missing_scan_types(tango_context, devices):
    logger.info("%s", tango_context)
    _, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, devices, ObsState.IDLE
    )
    scan_types_key = "scan_types"
    assign_input_str = get_assign_input_str()
    json_argument = json.loads(assign_input_str)
    del json_argument["execution_block"][scan_types_key]
    assert assign_res_command.check_allowed()
    (result_code, message) = assign_res_command.invoke_assign_resources(
        json.dumps(json_argument)
    )
    assert result_code == ResultCode.FAILED
    assert scan_types_key in message


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_assign_resources_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, devices, obsstate_value=ObsState.READY
    )
    cm.get_device().update_unresponsive(False)
    with pytest.raises(
        InvalidObsStateError,
        match="AssignResources command is not allowed in",
    ):
        assign_res_command.check_allowed()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_assign_resources_command_fail_check_allowed_with_device_unresponsive(  # noqa:E501
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, assign_res_command, _ = get_sdpsln_command_obj(
        AssignResources, devices, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        assign_res_command.check_allowed()
