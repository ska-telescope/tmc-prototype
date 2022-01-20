import time
from os.path import dirname, join

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory
from tango import DevState

from tests.integration.common import assert_event_arrived
from tests.settings import SLEEP_TIME, TIMEOUT, logger


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
    pytest.event_arrived = False

    def event_callback(evt):
        assert not evt.err
        logger.info(evt.attr_value.value)
        if evt.attr_value.value == ObsState.IDLE:
            pytest.event_arrived = True

    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpsal_node = dev_factory.get_device(sdpsaln_name)

    event_id = sdpsal_node.subscribe_event(
        "obsState",
        tango.EventType.CHANGE_EVENT,
        event_callback,
        stateless=True,
    )

    initial_len = len(sdpsal_node.commandExecuted)
    (result, unique_id) = sdpsal_node.TelescopeOn()
    (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
    sdp_subarray = dev_factory.get_device("mid_sdp/elt/subarray_01")
    sdp_subarray.SetDirectObsState(ObsState.IDLE)
    (result, unique_id) = sdpsal_node.Configure(configure_input_str)
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

    # sdp_subarray = dev_factory.get_device("mid_csp/elt/master")
    # sdp_subarray.SetDirectObsState(ObsState.IDLE)
    assert_event_arrived()
    sdpsal_node.unsubscribe_event(event_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
@pytest.mark.parametrize(
    "sdpsaln_name",
    [("ska_mid/tm_leaf_node/sdp_subarray01")],
)
def test_configure_command_mid(
    tango_context,
    sdpsaln_name,
):
    return configure(
        tango_context,
        sdpsaln_name,
        get_assign_input_str(
            join(
                dirname(__file__), "..", "data", "command_AssignResources.json"
            )
        ),
        get_configure_input_str(
            join(dirname(__file__), "..", "data", "command_Configure.json")
        ),
    )
