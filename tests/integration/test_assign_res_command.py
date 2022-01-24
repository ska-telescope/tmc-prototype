import time
from os.path import dirname, join

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, logger


def get_assign_input_str(assign_input_file="command_AssignResources.json"):
    path = join(dirname(__file__), "..", "data", assign_input_file)
    with open(path, "r") as f:
        assign_input_str = f.read()
    return assign_input_str


def assign_resouces(tango_context, sdpsaln_name, assign_input_str):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)

    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.TelescopeOn()
    (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    assert result[0] == ResultCode.QUEUED
    start_time = time.time()
    while len(sdpsal_node.commandExecuted) != initial_len + 2:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    for command in sdpsal_node.commandExecuted:
        if command[0] == unique_id[0]:
            logger.info("command result: %s", command)
            assert command[2] == "ResultCode.OK"

@pytest.mark.ncra
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "sdpsaln_name",
    [("ska_mid/tm_leaf_node/sdp_subarray01")],
)
def test_assign_res_command_mid(tango_context, sdpsaln_name):
    return assign_resouces(
        tango_context,
        sdpsaln_name,
        assign_input_str=get_assign_input_str(),
    )
