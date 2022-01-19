import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, logger


def init_command(tango_context, sdpsaln_name):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)
    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.TelescopeOn()
    assert result[0] == ResultCode.QUEUED

    # sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_01")
    # sdp_subarray.SetDirectState(DevState.OFF)

    start_time = time.time()
    while len(sdpsal_node.commandExecuted) != initial_len + 1:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
    print("Command Executed attr:", sdpsal_node.commandExecuted)

    for command in sdpsal_node.commandExecuted:
        if command[0] == unique_id[0]:
            assert command[2] == "ResultCode.OK"

    sdpsal_node.Init()
    assert len(sdpsal_node.commandExecuted) == 1
    # ensure_checked_devices(sdpsal_node)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "sdpsaln_name",
    [("ska_mid/tm_leaf_node/sdp_subarray01")],
)
def test_init_command_mid(tango_context, sdpsaln_name):
    init_command(tango_context, sdpsaln_name)
