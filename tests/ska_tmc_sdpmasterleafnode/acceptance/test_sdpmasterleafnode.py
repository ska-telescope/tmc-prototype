import json
import time
from os.path import dirname, join

import numpy as np
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from ska_tango_base.commands import ResultCode
from tango import Database, DeviceProxy
from tests.settings import SLEEP_TIME, logger

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
def subarray_node():
    database = Database()
    instance_list = database.get_device_exported_for_class("SdpMasterLeafNode")
    for instance in instance_list.value_string:
        return DeviceProxy(instance)


@when(parsers.parse("I call the command {command_name}"))
def call_command(sdpmasterleaf_node, command_name):
    try:
        pytest.command_result = sdpmasterleaf_node.command_inout(command_name)
    except Exception as ex:
        assert "CommandNotAllowed" in str(ex)
        pytest.command_result = "CommandNotAllowed"

@then(
    parsers.parse(
        "the command is queued and executed in less than {seconds} ss"
    )
)
def check_command(sdpmasterleaf_node, seconds):
    if pytest.command_result == "CommandNotAllowed":
        return

    assert pytest.command_result[0][0] == ResultCode.QUEUED
    unique_id = pytest.command_result[1][0]
    start_time = time.time()
    executed = False
    while not executed:
        for command in sdpmasterleaf_node.commandExecuted:
            if command[0] == unique_id:
                logger.info("command result: %s", command)
                assert (
                    command[2] == str(ResultCode.OK)
                    or command[2] == str(ResultCode.FAILED)
                    or command[2] == str(ResultCode.STARTED)
                )
                command_name = command[1]
                executed = True
        if executed:
            break
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > float(seconds):
            pytest.fail("Timeout occurred while executing the test")


scenarios("../ska_tmc_sdpmasterleafnode/features/sdpmasterleafnode.feature")
