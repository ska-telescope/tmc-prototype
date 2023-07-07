import time

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_LOW,
    SDP_SUBARRAY_LEAF_NODE_MID,
    event_remover,
    logger,
)


def off_command(
    tango_context, sdpsaln_fqdn, sdpsa_fqdn, change_event_callbacks
):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_fqdn)
    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )

    sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandsInQueue"],
    )
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        None, lookahead=3
    )
    result, unique_id = sdp_subarray_ln_proxy.On()
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        ("On",), lookahead=4
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
        lookahead=4,
    )

    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        None,
        lookahead=4,
    )
    result, unique_id = sdp_subarray_ln_proxy.Off()
    time.sleep(0.5)
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        ("Off",), lookahead=4
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=4,
    )

    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        None,
        lookahead=2,
    )
    event_remover(
        change_event_callbacks,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )


@pytest.mark.test1
@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_off_command_mid(tango_context, change_event_callbacks):
    off_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_off_command_low(tango_context, change_event_callbacks):
    off_command(
        tango_context,
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        change_event_callbacks,
    )
