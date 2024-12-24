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
)
from tests.settings import logger
from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down

dev_factory = DevFactory()


def configure_error_propogation(
    sdpsln_name,
    assign_input_str,
    configure_input_str,
    change_event_callbacks,
) -> None:
    dev_factory = DevFactory()
    sdpsln_device = dev_factory.get_device(sdpsln_name)

    if sdpsln_name == SDPSUBARRAYLEAFNODE_MID:
        sdp_subarray = dev_factory.get_device(MID_SDP_SUBARRAY)
    else:
        sdp_subarray = dev_factory.get_device(LOW_SDP_SUBARRAY)
    try:
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
        logger.info(
            f"Configure Command ID: {unique_id} Returned result: {result}"
        )

        assert unique_id[0].endswith("Configure")
        assert result[0] == ResultCode.QUEUED

        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            (unique_id[0], '[3, "Missing scan_type key"]'),
            lookahead=3,
        )
        tear_down(
            dev_factory, sdp_subarray, sdpsln_device, change_event_callbacks
        )
        sdpsln_device.unsubscribe_event(obsstate_id)
        sdpsln_device.unsubscribe_event(lrcr_id)
        sdp_subarray.ClearCommandCallInfo()

    except Exception as exception:
        tear_down(
            dev_factory, sdp_subarray, sdpsln_device, change_event_callbacks
        )
        sdpsln_device.unsubscribe_event(obsstate_id)
        sdpsln_device.unsubscribe_event(lrcr_id)
        sdp_subarray.ClearCommandCallInfo()
        raise Exception(exception)


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_configure_command_error_propagation_mid(
    json_factory,
    change_event_callbacks,
):
    return configure_error_propogation(
        SDPSUBARRAYLEAFNODE_MID,
        json_factory("command_AssignResources"),
        json_factory("command_Configure_without_ScanType"),
        change_event_callbacks,
    )


@pytest.mark.post_deployment
@pytest.mark.SKA_lowm
def test_configure_command_error_propagation_low(
    json_factory,
    change_event_callbacks,
):
    return configure_error_propogation(
        SDPSUBARRAYLEAFNODE_LOW,
        json_factory("command_AssignResources"),
        json_factory("command_Configure_without_ScanType"),
        change_event_callbacks,
    )
