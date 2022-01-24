import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, logger


def on_command(tango_context, sdpsaln_name):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)
    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.TelescopeOn()
    logger.info(result)
    logger.info(unique_id)
    assert result[0] == ResultCode.QUEUED
    start_time = time.time()
    while len(sdpsal_node.commandExecuted) != initial_len + 1:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    for command in sdpsal_node.commandExecuted:
        if command[0] == unique_id[0]:
            assert command[2] == "ResultCode.OK"

@pytest.mark.ncra
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_on_command_mid(tango_context):
    on_command(tango_context, "ska_mid/tm_leaf_node/sdp_subarray01")
