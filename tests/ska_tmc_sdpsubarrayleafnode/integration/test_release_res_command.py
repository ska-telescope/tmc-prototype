import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import event_remover, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def release_resources(
    tango_context, sdpsaln_name, device, json_factory, change_event_callbacks
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    # initial_len = len(sdp_subarray_ln_proxy.commandExecuted)
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
        lookahead=2,
    )

    # change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
    #     None,
    #     lookahead=4,
    # )

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

    # change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
    #     None,
    #     lookahead=6,
    # )

    result, unique_id = sdp_subarray_ln_proxy.ReleaseAllResources()
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        (
            "On",
            "AssignResources",
            "ReleaseResources",
        ),
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=6,
    )

    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )
    sdp_subarray = dev_factory.get_device(device)
    sdp_subarray.SetDirectObsState(ObsState.IDLE)
    assert sdp_subarray.obsState == ObsState.IDLE

    # if result[0] != ResultCode.QUEUED:
    #     logger.error("Result: %s message: %s", result[0], unique_id)
    # assert result[0] == ResultCode.QUEUED
    # start_time = time.time()
    # while len(sdp_subarray_ln_proxy.commandExecuted) != initial_len + 3:
    #     time.sleep(SLEEP_TIME)
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time > 100:
    #         pytest.fail("Timeout occurred while executing the test")
    #
    # for command in sdp_subarray_ln_proxy.commandExecuted:
    #     if command[0] == unique_id[0]:
    #         logger.info("command result: %s", command)
    #         assert command[2] == "ResultCode.OK"

    tear_down(dev_factory, sdp_subarray)


@pytest.mark.rel_1
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
def test_release_res_command_low(tango_context, device, json_factory):
    return release_resources(
        tango_context,
        "ska_low/tm_leaf_node/sdp_subarray01",
        device,
        json_factory,
    )
