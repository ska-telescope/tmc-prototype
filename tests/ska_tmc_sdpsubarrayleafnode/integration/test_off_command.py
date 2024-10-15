import time

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import COMMAND_COMPLETED
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_LOW,
    SDP_SUBARRAY_LEAF_NODE_MID,
    logger,
)


def off_command(sdpsaln_fqdn, sdpsa_fqdn, change_event_callbacks):
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_fqdn)

    lrcr_in_que_id = sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandsInQueue"],
    )
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        (), lookahead=2
    )
    result, unique_id = sdp_subarray_ln_proxy.On()
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        ("On",), lookahead=4
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED
    lrcr_id = sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )

    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        (),
    )
    result, unique_id = sdp_subarray_ln_proxy.Off()
    time.sleep(0.5)
    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        ("Off",), lookahead=2
    )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=6,
    )

    change_event_callbacks["longRunningCommandsInQueue"].assert_change_event(
        (),
    )

    sdp_subarray_ln_proxy.unsubscribe_event(lrcr_in_que_id)
    sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_off_command_mid(change_event_callbacks):
    off_command(
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_off_command_low(change_event_callbacks):
    off_command(
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        change_event_callbacks,
    )
