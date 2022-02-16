import time
from os.path import dirname, join

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import SLEEP_TIME, TIMEOUT, logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


def get_assign_input_str(path):
    with open(path, "r") as f:
        assign_input_str = f.read()
    return assign_input_str


def get_configure_input_str(path):
    with open(path, "r") as f:
        configure_input_str = f.read()
    return configure_input_str


def configure(
    tango_context,
    sdpsaln_name,
    assign_input_str,
    configure_input_str,
):

    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)

    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.On()
    (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
    sdp_subarray.SetDirectObsState(ObsState.IDLE)
    assert sdp_subarray.obsState == ObsState.IDLE
    time.sleep(SLEEP_TIME)
    (result, unique_id) = sdpsal_node.Configure(configure_input_str)
    sdp_subarray.SetDirectObsState(ObsState.READY)
    assert sdp_subarray.obsState == ObsState.READY
    # time.sleep(SLEEP_TIME)
    # (result, unique_id) = sdpsal_node.End()
    # sdp_subarray.SetDirectObsState(ObsState.IDLE)
    # assert sdp_subarray.obsState == ObsState.IDLE
    # time.sleep(SLEEP_TIME)
    # (result, unique_id) = sdpsal_node.ReleaseResources(configure_input_str)
    # sdp_subarray.SetDirectObsState(ObsState.EMPTY)
    # assert sdp_subarray.obsState == ObsState.EMPTY

    assert result[0] == ResultCode.QUEUED
    start_time = time.time()
    while len(sdpsal_node.commandExecuted) != initial_len + 3:
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    for command in sdpsal_node.commandExecuted:
        if command[0] == unique_id[0]:
            logger.info("command result: %s", command)
            assert command[2] == "ResultCode.OK"

    tear_down(dev_factory, sdp_subarray)

# def tear_down(dev_factory, sdp_subarray):
#     sdp_subarray = dev_factory.get_device(sdp_subarray)
#     sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
#     logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

#     if sdp_subarray_obsstate.value == 0:
#         sdp_subarray.Off()

#     if sdp_subarray_obsstate.value == 2:
#         sdp_subarray.ReleaseResources()
#         sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
#         sdp_subarray.SetDirectObsState(ObsState.EMPTY)
#         time.sleep(0.5)
#         sdp_subarray.Off()
#         # sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
#         # logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

#     if sdp_subarray_obsstate.value == 4 or 5:
#         sdp_subarray.Abort()
#         sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
#         sdp_subarray.SetDirectObsState(ObsState.ABORTED)
#         time.sleep(1)
#         sdp_subarray.Restart()
#         sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
#         sdp_subarray.SetDirectObsState(ObsState.EMPTY)
#         time.sleep(1)
#         sdp_subarray.Off()
#         # sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
#         # logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")

#     if sdp_subarray_obsstate.value == 7:
#         sdp_subarray.Restart()
#         sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_1")
#         sdp_subarray.SetDirectObsState(ObsState.EMPTY)
#         time.sleep(1)
#         sdp_subarray.Off()
#         # sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
#         # logger.info(f"SDP Subarray ObsState: {sdp_subarray_obsstate.value}")


@pytest.mark.ncra
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "sdpsaln_name",
    [("ska_mid/tm_leaf_node/sdp_subarray01")],
)
def test_configure_command(
    tango_context,
    sdpsaln_name,
):
    return configure(
        tango_context,
        sdpsaln_name,
        get_assign_input_str(
            join(
                dirname(__file__),
                "..",
                "..",
                "data",
                "command_AssignResources.json",
            )
        ),
        get_configure_input_str(
            join(
                dirname(__file__), "..", "..", "data", "command_Configure.json"
            )
        ),
    )
