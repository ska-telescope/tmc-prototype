import time
from os.path import dirname, join

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.dev_factory import DevFactory
from tango import Database, DeviceProxy

from tests.settings import SLEEP_TIME, TIMEOUT, logger


def get_json_input_str(path):
    with open(path, "r") as f:
        input_json_str = f.read()
    return input_json_str


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
    dev_factory = DevFactory()
    if "ska_mid" in sdpsubarrayleaf_node.dev_name():

        sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")
    else:
        sdp_subarray = dev_factory.get_device("low-sdp/subarray/01")
    try:
        if command_name == "AssignResources":
            logger.info(
                f"sdpsubarrayleaf_node: {sdpsubarrayleaf_node.dev_name()}"
            )
            assign_res_string = get_json_input_str(
                join(
                    dirname(__file__),
                    "..",
                    "..",
                    "data",
                    "command_AssignResources.json",
                )
            )
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.EMPTY)
            assert sdp_subarray.obsState == ObsState.EMPTY
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, assign_res_string
            )
        elif command_name == "Configure":
            configure_string = get_json_input_str(
                join(
                    dirname(__file__),
                    "..",
                    "..",
                    "data",
                    "command_Configure.json",
                )
            )
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.IDLE)
            assert sdp_subarray.obsState == ObsState.IDLE
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, configure_string
            )
        elif command_name == "Scan":
            scan_string = get_json_input_str(
                join(
                    dirname(__file__), "..", "..", "data", "command_Scan.json"
                )
            )
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.READY)
            assert sdp_subarray.obsState == ObsState.READY
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, scan_string
            )
        elif command_name == "EndScan":
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.SCANNING)
            assert sdp_subarray.obsState == ObsState.SCANNING
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        elif command_name == "End":
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.READY)
            assert sdp_subarray.obsState == ObsState.READY
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        elif command_name == "Abort":
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.IDLE)
            assert sdp_subarray.obsState == ObsState.IDLE
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        elif command_name == "ObsReset":
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.ABORTED)
            assert sdp_subarray.obsState == ObsState.ABORTED
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
        elif command_name == "ReleaseResources":
            check_sdp_subarray_obsstate(sdp_subarray, ObsState.IDLE)
            assert sdp_subarray.obsState == ObsState.IDLE
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name, ""
            )
        else:
            pytest.command_result = sdpsubarrayleaf_node.command_inout(
                command_name
            )
    except Exception as ex:
        assert "CommandNotAllowed" in str(ex)
        pytest.command_result = "CommandNotAllowed"


@then(
    parsers.parse(
        "the command is queued and executed in less than {seconds} ss"
    )
)
def check_command(sdpsubarrayleaf_node, seconds):
    if pytest.command_result == "CommandNotAllowed":
        return

    assert pytest.command_result[0][0] == ResultCode.QUEUED
    unique_id = pytest.command_result[1][0]
    start_time = time.time()
    executed = False
    while not executed:
        for command in sdpsubarrayleaf_node.commandExecuted:
            if command[0] == unique_id:
                logger.info("command result: %s", command)
                assert (
                    command[2] == str(ResultCode.OK)
                    or command[2] == str(ResultCode.FAILED)
                    or command[2] == str(ResultCode.STARTED)
                )
                executed = True
        if executed:
            break
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > float(seconds):
            pytest.fail("Timeout occurred while executing the test")


def check_sdp_subarray_obsstate(sdp_subarray, obs_state):
    sdp_subarray_obsstate = sdp_subarray.read_attribute("obsState")
    logger.info(f"SDP Subarray Device : {sdp_subarray}")
    logger.info(f"SDP Subarray obsState is {sdp_subarray_obsstate}")
    logger.info(f"In SDP Subarray Device : {sdp_subarray},checking ObsState")
    wait_time = 0
    while (sdp_subarray_obsstate.value) != obs_state:
        time.sleep(SLEEP_TIME)
        obsstate_val = sdp_subarray.read_attribute("obsState")
        logger.info(f"Current SDP Subarray obsState is: {obsstate_val.value}")
        logger.info(f"Expected SDP Subarray obsState is : {obs_state}")
        wait_time = wait_time + 1
        logger.info(f"wait_time in teardown  {wait_time}")
        if wait_time > TIMEOUT:
            pytest.fail(
                "Timeout occurred in transitioning SDP Subarray obsState to"
                + "{}".format(sdp_subarray_obsstate.value)
            )


scenarios(
    "../ska_tmc_sdpsubarrayleafnode/features/sdpsubarrayleafnode.feature"
)
