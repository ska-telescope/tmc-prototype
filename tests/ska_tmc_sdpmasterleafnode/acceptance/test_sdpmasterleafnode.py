import pytest
import tango
from pytest_bdd import given, parsers, scenarios, then, when
from ska_tango_base.commands import ResultCode
from tango import Database, DeviceProxy

from tests.conftest import COMMAND_COMPLETED


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
    instance_list = database.get_device_exported_for_class("LowTmcLeafNodeSdp")
    for instance in instance_list.value_string:
        return DeviceProxy(instance)
    instance_list = database.get_device_exported_for_class("MidTmcLeafNodeSdp")
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
    lrcr_id = sdpmasterleaf_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )

    group_callback["longRunningCommandResult"].assert_change_event(
        (unique_id, COMMAND_COMPLETED), lookahead=2
    )

    sdpmasterleaf_node.unsubscribe_event(lrcr_id)


scenarios("../ska_tmc_sdpmasterleafnode/features/sdpmasterleafnode.feature")
