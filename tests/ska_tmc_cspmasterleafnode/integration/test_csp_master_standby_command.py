import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, logger


def standby_command(tango_context, cspmln_name):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    cspmln_node = dev_factory.get_device(cspmln_name)
    initial_len = len(cspmln_node.commandExecuted)
    (result, unique_id) = cspmln_node.On()
    (result, unique_id) = cspmln_node.Standby()
    logger.info(result)
    logger.info(unique_id)
    assert result[0] == ResultCode.QUEUED
    start_time = time.time()
    while len(cspmln_node.commandExecuted) != initial_len + 2:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    for command in cspmln_node.commandExecuted:
        if command[0] == unique_id[0]:
            assert command[2] == "ResultCode.OK"


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_standby_command_mid(tango_context):
    standby_command(tango_context, "ska_mid/tm_leaf_node/csp_master")
