import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def assign_resouces(tango_context, sdpsaln_fqdn, change_event_callbacks):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    # sdp_subarray = dev_factory.get_device(sdp_subarray)
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_fqdn)

    # initial_len = len(sdpsal_node.commandExecuted)
    # (result, unique_id) = sdpsal_node.On()
    # assign_input_str = json_factory("command_AssignResources")
    # (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    # assert result[0] == ResultCode.QUEUED
    # start_time = time.time()
    # while len(sdpsal_node.commandExecuted) != initial_len + 2:
    #     time.sleep(SLEEP_TIME)
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time > TIMEOUT:
    #         pytest.fail("Timeout occurred while executing the test")

    # for command in sdpsal_node.commandExecuted:
    #     if command[0] == unique_id[0]:
    #         logger.info("command result: %s", command)
    #         assert command[2] == "ResultCode.STARTED"

    sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandsInQueue"],
    )
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        None,
    )
    result, unique_id = sdp_subarray_ln_proxy.On()
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        ("On",),
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
        lookahead=2,
    )

    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        None,
        lookahead=2,
    )

    tear_down(dev_factory, sdp_subarray_ln_proxy)


@pytest.mark.assigntest10
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    ["sdpsaln_name"],
    [("ska_mid/tm_leaf_node/sdp_subarray01")],
)
def test_assign_res_command_mid(tango_context, sdpsaln_name, json_factory):
    return assign_resouces(
        tango_context,
        sdpsaln_name,
        json_factory,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
@pytest.mark.parametrize(
    ["sdpsaln_name"],
    [("ska_low/tm_leaf_node/sdp_subarray01")],
)
def test_assign_res_command_low(tango_context, sdpsaln_name, json_factory):
    return assign_resouces(
        tango_context,
        sdpsaln_name,
        json_factory,
    )
