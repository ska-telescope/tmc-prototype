import pytest
import tango
from pytest_bdd import given, parsers, scenarios, then, when
from ska_tango_base.commands import ResultCode
from tango import Database, DeviceProxy

from tests.settings import event_remover


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
def call_command(sdpsubarrayleaf_node, command_name):
    try:
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
def check_command(sdpsubarrayleaf_node, group_callback):
    if pytest.command_result == "CommandNotAllowed":
        return

    assert pytest.command_result[0][0] == ResultCode.QUEUED
    unique_id = pytest.command_result[1][0]
    sdpsubarrayleaf_node.subscribe_event(
        "longRunningCommandIDsInQueue",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandIDsInQueue"],
    )
    sdpsubarrayleaf_node.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandsInQueue"],
    )
    sdpsubarrayleaf_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    group_callback["longRunningCommandIDsInQueue"].assert_change_event(
        (str(unique_id),),
    )

    group_callback["longRunningCommandResult"].assert_change_event(
        (unique_id, str(int(ResultCode.OK))), lookahead=2
    )

    group_callback["longRunningCommandsInQueue"].assert_change_event(
        None,
        lookahead=2,
    )
    event_remover(
        group_callback,
        ["longRunningCommandResult", "longRunningCommandsInQueue"],
    )


scenarios(
    "../ska_tmc_sdpsubarrayleafnode/features/sdpsubarrayleafnode.feature"
)
