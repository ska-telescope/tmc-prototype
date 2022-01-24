import time

import mock
import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.assign_resources_command import (
    AssignResources,
)
from ska_tmc_sdpsubarrayleafnode.commands.telescope_on_command import (
    TelescopeOn,
)
from ska_tmc_sdpsubarrayleafnode.manager.command_executor import (
    CommandExecutor,
)
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import SLEEP_TIME, TIMEOUT, create_cm, logger
from tests.unit.commands.test_assign_resources_command import (
    get_assign_input_str,
)


def test_command_executor(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    executor = CommandExecutor(logger)
    my_adapter_factory = HelperAdapterFactory()
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    executor.enqueue_command(on_command, None)
    executor.enqueue_command(on_command, None)
    executor.enqueue_command(on_command, None)
    start_time = time.time()
    while 3 != len(executor.command_executed):
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        time.sleep(SLEEP_TIME)

    for command_result in executor.command_executed:
        assert command_result["Command"] == "TelescopeOn"
        assert command_result["ResultCode"] == ResultCode.OK
        assert command_result["Message"] == ""

    assert executor.command_in_progress == "None"
    assert not executor.queue_full
    executor.stop()


def test_command_with_argin_executor(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    executor = CommandExecutor(logger)

    my_adapter_factory = HelperAdapterFactory()
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assign_input_str = get_assign_input_str()
    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)
    my_adapter_factory = HelperAdapterFactory()
    assign_command = AssignResources(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    initial_len = len(executor.command_executed)
    executor.enqueue_command(on_command, None)
    executor.enqueue_command(assign_command, assign_input_str)
    start_time = time.time()
    while initial_len + 2 != len(executor.command_executed):
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        time.sleep(SLEEP_TIME)

    for command_result in executor.command_executed:
        assert command_result["Command"] == "TelescopeOn" or "AssignResources"
        assert command_result["ResultCode"] == ResultCode.OK
        assert command_result["Message"] == ""

    assert executor.command_in_progress == "None"
    assert not executor.queue_full


def testcommand_executor_raise_exception(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    executor = CommandExecutor(logger)
    attrs = {"do.side_effect": Exception}
    on_command = mock.Mock(**attrs)
    executor.enqueue_command(on_command, None)
    start_time = time.time()
    while 1 != len(executor.command_executed):
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        time.sleep(SLEEP_TIME)

    for command_result in executor.command_executed:
        assert command_result["Command"] == "Mock"
        assert command_result["ResultCode"] == ResultCode.FAILED

    assert executor.command_in_progress == "None"
