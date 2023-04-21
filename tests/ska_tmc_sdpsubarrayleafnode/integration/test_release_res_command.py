import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def release_resources(tango_context, sdpsaln_name, device, json_factory):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)
    initial_len = len(sdpsal_node.commandExecuted)
    assign_input_str = json_factory("command_AssignResources")
    (result, unique_id) = sdpsal_node.On()
    (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    sdp_subarray = dev_factory.get_device(device)
    sdp_subarray.SetDirectObsState(ObsState.IDLE)
    assert sdp_subarray.obsState == ObsState.IDLE

    (result, unique_id) = sdpsal_node.ReleaseResources("")
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

    tear_down(dev_factory, sdp_subarray)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "device",
    [("mid-sdp/subarray/01")],
)
def test_release_res_command_mid(tango_context, device, json_factory):
    return release_resources(
        tango_context,
        "ska_mid/tm_leaf_node/sdp_subarray01",
        device,
        json_factory,
    )


@pytest.mark.skip
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
