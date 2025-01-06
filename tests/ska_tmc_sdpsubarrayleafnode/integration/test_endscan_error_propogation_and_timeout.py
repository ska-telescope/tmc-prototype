"""Test cases for testing timeout and Error Propagation on EndScan command."""

from typing import Callable

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import (
    COMMAND_COMPLETED,
    LOW_SDP_SUBARRAY,
    MID_SDP_SUBARRAY,
    SDPSUBARRAYLEAFNODE_LOW,
    SDPSUBARRAYLEAFNODE_MID,
    TIMEOUT_EXCEPTION,
)
from tests.settings import (
    ENDSCAN_TIMEOUT,
    FAILED_RESULT_DEFECT,
    RESET_DEFECT,
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    SDP_SUBARRAY_LEAF_NODE_LOW,
    SDP_SUBARRAY_LEAF_NODE_MID,
    logger,
)
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down

dev_factory = DevFactory()


def endscan_error_propogation(
    sdpsln_name,
    sdp_device,
    assign_input_str,
    configure_input_str,
    scan_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsln_device = dev_factory.get_device(sdpsln_name)
    sdp_subarray = dev_factory.get_device(sdp_device)

    result, unique_id = sdpsln_device.AssignResources(assign_input_str)
    logger.info(
        f"AssignResources Command ID: {unique_id} Returned \
            result: {result}"
    )

    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED

    lrcr_id = sdpsln_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=3,
    )
    obsstate_id = sdpsln_device.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.IDLE,
        lookahead=4,
    )
    result, unique_id = sdpsln_device.Configure(configure_input_str)
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=6,
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.READY,
        lookahead=4,
    )
    result, unique_id = sdpsln_device.Scan(scan_input_str)

    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=6,
    )

    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.SCANNING,
        lookahead=4,
    )
    sdp_subarray.SetDefective(FAILED_RESULT_DEFECT)
    result, unique_id = sdpsln_device.EndScan()

    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED
    SDP_ERROR = (
        '[3, "The invocation of the EndScan command is failed on '
        + f"SDP Subarray Device {sdp_device} Reason: Error in invoking "
        "EndScan command on SDP Subarray.The command has NOT been executed. "
        'This device will continue with normal operation."]'
    )

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (
            unique_id[0],
            SDP_ERROR,
        ),
        lookahead=6,
    )
    sdp_subarray.SetDefective(RESET_DEFECT)
    tear_down(dev_factory, sdp_subarray, sdpsln_device, change_event_callbacks)
    sdpsln_device.unsubscribe_event(obsstate_id)
    sdpsln_device.unsubscribe_event(lrcr_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_endscan_command_error_propagation_mid(
    json_factory,
    change_event_callbacks,
):
    return endscan_error_propogation(
        SDPSUBARRAYLEAFNODE_MID,
        MID_SDP_SUBARRAY,
        json_factory("command_AssignResources"),
        json_factory("command_Configure"),
        json_factory("command_Scan"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_endscan_command_error_propagation_low(
    json_factory,
    change_event_callbacks,
):
    return endscan_error_propogation(
        SDPSUBARRAYLEAFNODE_LOW,
        LOW_SDP_SUBARRAY,
        json_factory("command_AssignResources"),
        json_factory("command_Configure"),
        json_factory("command_Scan"),
        change_event_callbacks,
    )


def endscan_timeout(
    sdpsaln_name: str,
    device: str,
    json_factory: Callable,
    change_event_callbacks: dict,
):
    dev_factory = DevFactory()
    sdp_subarray_ln_proxy = dev_factory.get_device(sdpsaln_name)
    sdp_subarray = dev_factory.get_device(device)

    lrcr_id = sdp_subarray_ln_proxy.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    obsstate_id = sdp_subarray_ln_proxy.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )

    result, unique_id = sdp_subarray_ln_proxy.On()
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )
    assign_input_str = json_factory("command_AssignResources")
    result, unique_id = sdp_subarray_ln_proxy.AssignResources(assign_input_str)
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=4,
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.IDLE,
        lookahead=4,
    )

    configure_input_str = json_factory("command_Configure")
    result, unique_id = sdp_subarray_ln_proxy.Configure(configure_input_str)
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=6,
    )
    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.READY,
        lookahead=4,
    )
    scan_input_str = json_factory("command_Scan")
    result, unique_id = sdp_subarray_ln_proxy.Scan(scan_input_str)

    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=6,
    )

    change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
        ObsState.SCANNING,
        lookahead=4,
    )
    sdp_subarray.SetDelayInfo(ENDSCAN_TIMEOUT)
    result, unique_id = sdp_subarray_ln_proxy.EndScan()

    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (
            unique_id[0],
            TIMEOUT_EXCEPTION,
        ),
        lookahead=3,
    )
    sdp_subarray.ResetDelayInfo()
    tear_down(
        dev_factory,
        sdp_subarray,
        sdp_subarray_ln_proxy,
        change_event_callbacks,
    )
    sdp_subarray_ln_proxy.unsubscribe_event(lrcr_id)
    sdp_subarray_ln_proxy.unsubscribe_event(obsstate_id)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_endscan_command_timeout_mid(json_factory, change_event_callbacks):
    return endscan_timeout(
        SDP_SUBARRAY_LEAF_NODE_MID,
        SDP_SUBARRAY_DEVICE_MID,
        json_factory,
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_endscan_command_timeout_low(json_factory, change_event_callbacks):
    return endscan_timeout(
        SDP_SUBARRAY_LEAF_NODE_LOW,
        SDP_SUBARRAY_DEVICE_LOW,
        json_factory,
        change_event_callbacks,
    )