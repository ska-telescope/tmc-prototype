import time
from os.path import dirname, join

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, logger


def get_input_str(path):
    with open(path, "r") as f:
        assign_input_str = f.read()
    return assign_input_str


def release_resources(tango_context, sdpsaln_name, assign_input_str):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)
    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.TelescopOn()
    (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    (result, unique_id) = sdpsal_node.ReleaseResources()
    if result[0] != ResultCode.QUEUED:
        logger.error("Result: %s message: %s", result[0], unique_id)
    assert result[0] == ResultCode.QUEUED
    start_time = time.time()
    while len(sdpsal_node.commandExecuted) != initial_len + 3:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > 100:
            pytest.fail("Timeout occurred while executing the test")

    for command in sdpsal_node.commandExecuted:
        if command[0] == unique_id[0]:
            logger.info("command result: %s", command)
            assert command[2] == "ResultCode.OK"


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_release_res_command_mid(tango_context):
    return release_resources(
        tango_context,
        "ska_mid/tm_central/central_node",
        get_input_str(
            join(
                dirname(__file__), "..", "data", "command_AssignResources.json"
            )
        ),
    )
