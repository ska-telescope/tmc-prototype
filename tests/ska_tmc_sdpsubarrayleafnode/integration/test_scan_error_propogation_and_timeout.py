import json

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import COMMAND_COMPLETED
from tests.settings import FAILED_RESULT_DEFECT, RESET_DEFECT, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def scan(sdpsaln_name, device, json_factory, change_event_callbacks):
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(device)

    lrcr_id = sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    obsstate_id = sdp_subarray_ln_proxy.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )
    result, unique_id = sdp_subarray_ln_proxy.On()
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )
    assign_input_str = json_factory("command_AssignResources")
    result, unique_id = sdp_subarray_ln_proxy.AssignResources(assign_input_str)

    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.IDLE,
        lookahead=4,
    )

    configure_input_str = json_factory("command_Configure")
    result, unique_id = sdp_subarray_ln_proxy.Configure(configure_input_str)
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=6,
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.READY,
        lookahead=4,
    )
    sdp_subarray.SetDefective(FAILED_RESULT_DEFECT)
    scan_input_str = json_factory("command_Scan")
    invalid_scan_str = json.loads(scan_input_str)
    scan_input_str = invalid_scan_str.pop("scan_id")
    result, unique_id = sdp_subarray_ln_proxy.Scan(json.dumps(scan_input_str))

    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], '[3, ""]'),
        lookahead=6,
    )
    sdp_subarray.SetDefective(RESET_DEFECT)

    tear_down(
        dev_factory,
        sdp_subarray,
        sdp_subarray_ln_proxy,
        change_event_callbacks,
    )
    sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
    sdp_subarray_ln_proxy.unsubscribe_event(obsstate_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "device",
    [("mid-sdp/subarray/01")],
)
def test_scan_command_mid(device, json_factory, change_event_callbacks):
    return scan(
        "ska_mid/tm_leaf_node/sdp_subarray01",
        device,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@pytest.mark.parametrize(
    "device",
    [("low-sdp/subarray/01")],
)
def test_scan_command_low(
    device,
    json_factory,
    change_event_callbacks,
):
    return scan(
        "ska_low/tm_leaf_node/sdp_subarray01",
        device,
        json_factory,
        change_event_callbacks,
    )
