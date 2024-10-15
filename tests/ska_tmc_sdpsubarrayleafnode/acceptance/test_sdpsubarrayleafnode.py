import pytest
import tango
from pytest_bdd import given, parsers, scenarios, then, when
from ska_control_model import HealthState, ObsState
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory
from tango import Database, DeviceProxy

from tests.conftest import COMMAND_COMPLETED
from tests.settings import logger


@given(
    "a TANGO ecosystem with a set of devices deployed",
    target_fixture="device_list",
)
def device_list():
    db = Database()
    return db.get_device_exported("*")


@given(
    parsers.parse("a SdpSubarrayLeafNode device"),
    target_fixture="sdpsubarrayleaf_node",
)
def sdpsubarrayleaf_node():
    database = Database()
    instance_list = database.get_device_exported_for_class(
        "SdpSubarrayLeafNode"
    )
    for instance in instance_list.value_string:
        return DeviceProxy(instance)


@when(parsers.parse("I call the command {command_name}"))
def call_command(
    sdpsubarrayleaf_node, command_name: str, json_factory
) -> None:
    try:
        if command_name == "AssignResources":
            logger.info(
                f"sdpsubarrayleaf_node: {sdpsubarrayleaf_node.dev_name()}"
            )
            assign_res_string = json_factory("command_AssignResources")
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, assign_res_string
            )
        elif command_name == "Configure":
            logger.info(
                f"sdpsubarrayleaf_node: {sdpsubarrayleaf_node.dev_name()}"
            )
            configure_string = json_factory("command_Configure")
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, configure_string
            )
        elif command_name == "Scan":
            logger.info(
                f"sdpsubarrayleaf_node: {sdpsubarrayleaf_node.dev_name()}"
            )
            scan_string = json_factory("command_Scan")
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, scan_string
            )
        elif command_name == "EndScan":
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        elif command_name == "End":
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        elif command_name == "ReleaseAllResources":
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        else:
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
    except Exception as ex:
        assert "DeviceUnresponsive" in str(ex)
        pytest.command_result = "DeviceUnresponsive"


@then(
    parsers.parse(
        "the command is queued and executed in less than {seconds} ss"
    )
)
def check_command(
    sdpsubarrayleaf_node, command_name: str, change_event_callbacks
) -> None:
    dev_factory = DevFactory()

    sdpsubarrayleaf_node_dev = dev_factory.get_device(sdpsubarrayleaf_node)
    sdp_subarray_leafnode_healthState = (
        sdpsubarrayleaf_node_dev.read_attribute("healthState").value
    )
    logger.info(
        "Current SdpSubarray leaf node healthstate is {}".format(
            sdp_subarray_leafnode_healthState
        )
    )
    assert sdp_subarray_leafnode_healthState == HealthState.OK

    if pytest.command_result == "CommandNotAllowed":
        return

    assert pytest.command_result[0][0] == ResultCode.QUEUED
    unique_id = pytest.command_result[1][0]

    assert unique_id.endswith(str(command_name))
    lrcr_id = sdpsubarrayleaf_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    obsstate_id = sdpsubarrayleaf_node_dev.subscribe_event(
        "sdpSubarrayObsState",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["sdpSubarrayObsState"],
    )

    if command_name == "AssignResources":
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.IDLE,
            lookahead=4,
        )

    elif command_name == "Configure":
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.READY,
            lookahead=4,
        )

    elif command_name == "Scan":
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.SCANNING,
            lookahead=4,
        )

    elif command_name == "EndScan":
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.READY,
            lookahead=4,
        )

    elif command_name == "End":
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.IDLE,
            lookahead=4,
        )

    elif command_name == "ReleaseAllResources":
        change_event_callbacks["sdpSubarrayObsState"].assert_change_event(
            ObsState.EMPTY,
            lookahead=4,
        )

    sdpsubarrayleaf_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )

    change_event_callbacks["longRunningCommandResult"].assert_change_event(
        (unique_id, COMMAND_COMPLETED),
        lookahead=4,
    )

    sdpsubarrayleaf_node_dev.unsubscribe_event(obsstate_id)
    sdpsubarrayleaf_node_dev.unsubscribe_event(lrcr_id)


scenarios(
    "../ska_tmc_sdpsubarrayleafnode/features/sdpsubarrayleafnode.feature"
)
