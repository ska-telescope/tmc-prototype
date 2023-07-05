import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import event_remover, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import (
    tear_down,
    wait_for_final_sdp_subarray_obsstate,
)


def release_resources(
    tango_context, sdpsaln_name, device, json_factory, change_event_callbacks
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(device)
    sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandsInQueue"],
    )

    sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )

    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        None,
    )
    result, unique_id = sdp_subarray_ln_proxy.On()
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        ("On",),
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=3,
    )
    assign_input_str = json_factory("command_AssignResources")
    result, unique_id = sdp_subarray_ln_proxy.AssignResources(assign_input_str)
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        (
            "On",
            "AssignResources",
        ),
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=4,
    )
    wait_for_final_sdp_subarray_obsstate(sdp_subarray_ln_proxy, ObsState.IDLE)
    result, unique_id = sdp_subarray_ln_proxy.ReleaseAllResources()
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        (
            "On",
            "AssignResources",
            "ReleaseAllResources",
        ),
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=6,
    )

    wait_for_final_sdp_subarray_obsstate(sdp_subarray_ln_proxy, ObsState.EMPTY)
    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )
    tear_down(dev_factory, sdp_subarray)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "device",
    [("mid-sdp/subarray/01")],
)
def test_release_res_command_mid(
    tango_context, device, json_factory, change_event_callbacks
):
    return release_resources(
        tango_context,
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
def test_release_res_command_low(
    tango_context,
    device,
    json_factory,
    change_event_callbacks,
):
    return release_resources(
        tango_context,
        "ska_low/tm_leaf_node/sdp_subarray01",
        device,
        json_factory,
        change_event_callbacks,
    )
