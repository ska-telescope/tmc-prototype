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
    parsers.parse("a SdpMasterLeafNode device"),
    target_fixture="sdpmasterleaf_node",
)
def sdpmasterleaf_node():
    database = Database()
    instance_list = database.get_device_exported_for_class("SdpMasterLeafNode")
    for instance in instance_list.value_string:
        return DeviceProxy(instance)


@when(parsers.parse("I call the command {command_name}"))
def call_command(sdpmasterleaf_node, command_name):
    try:
        pytest.command_result = sdpmasterleaf_node.command_inout(command_name)
    except Exception as ex:
        assert "DeviceUnresponsive" in str(ex)
        pytest.command_result = "DeviceUnresponsive"


@then(
    parsers.parse(
        "the command is queued and executed in less than {seconds} ss"
    )
)
def check_command(sdpmasterleaf_node, group_callback):
    if pytest.command_result == "CommandNotAllowed":
        return

    assert pytest.command_result[0][0] == ResultCode.QUEUED
    unique_id = pytest.command_result[1][0]
    sdpmasterleaf_node.subscribe_event(
        "longRunningCommandIDsInQueue",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandIDsInQueue"],
    )
    sdpmasterleaf_node.subscribe_event(
        "longRunningCommandsInQueue",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandsInQueue"],
    )
    sdpmasterleaf_node.subscribe_event(
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
    # start_time = time.time()
    # executed = False
    # while not executed:
    #     for command in sdpmasterleaf_node.commandExecuted:
    #         if command[0] == unique_id:
    #             logger.info("command result: %s", command)
    #             assert (
    #                 command[2] == str(ResultCode.OK)
    #                 or command[2] == str(ResultCode.FAILED)
    #                 or command[2] == str(ResultCode.STARTED)
    #             )
    #             executed = True
    #     if executed:
    #         break
    #     time.sleep(SLEEP_TIME)
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time > float(seconds):
    #         pytest.fail("Timeout occurred while executing the test")


scenarios("../ska_tmc_sdpmasterleafnode/features/sdpmasterleafnode.feature")
