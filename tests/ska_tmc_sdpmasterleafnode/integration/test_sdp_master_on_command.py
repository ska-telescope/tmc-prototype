import time

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, event_remover, logger


def on_command(tango_context, sdpmln_name, group_callback):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpmln_node = dev_factory.get_device(sdpmln_name)
    sdpmln_node.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandsInQueue"],
    )
    group_callback["longRunningCommandsInQueue"].assert_change_event(
        None,
    )
    # initial_len = len(sdpmln_node.commandExecuted)
    # availablity_value = sdpmln_node.read_attribute(
    #     "isSubsystemAvailable"
    # ).value
    # assert availablity_value
    result, unique_id = sdpmln_node.On()
    logger.info(result)
    logger.info(unique_id)
    # assert result[0] == ResultCode.QUEUED
    # start_time = time.time()
    # while len(sdpmln_node.commandExecuted) != initial_len + 1:
    #     time.sleep(SLEEP_TIME)
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time > TIMEOUT:
    #         pytest.fail("Timeout occurred while executing the test")

    # for command in sdpmln_node.commandExecuted:
    #     if command[0] == unique_id[0]:
    #         assert command[2] == "ResultCode.OK"
    group_callback["longRunningCommandsInQueue"].assert_change_event(
        ("On",),
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED
    sdpmln_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    group_callback["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=2,
    )

    group_callback["longRunningCommandsInQueue"].assert_change_event(
        None,
        lookahead=2,
    )
    event_remover(
        group_callback,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )


@pytest.mark.ontest5
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_on_command_mid(tango_context, group_callback):
    on_command(
        tango_context, "ska_mid/tm_leaf_node/sdp_master", group_callback
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_on_command_low(tango_context, group_callback):
    on_command(
        tango_context, "ska_low/tm_leaf_node/sdp_master", group_callback
    )
