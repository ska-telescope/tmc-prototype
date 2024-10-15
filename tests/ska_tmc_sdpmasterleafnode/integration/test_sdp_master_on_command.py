import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tmc_common.dev_factory import DevFactory

from tests.conftest import COMMAND_COMPLETED
from tests.settings import (
    SDP_MASTER_LEAF_DEVICE_LOW,
    SDP_MASTER_LEAF_DEVICE_MID,
    logger,
)


def on_command(tango_context, sdpmln_name, group_callback):
    logger.info("%s", tango_context)
    dev_factory = DevFactory()
    sdpmln_node = dev_factory.get_device(sdpmln_name)

    availablity_value = sdpmln_node.read_attribute(
        "isSubsystemAvailable"
    ).value
    assert availablity_value

    # lrcq_id = sdpmln_node.subscribe_event(
    #     "longRunningCommandsInQueue",
    #     tango.EventType.CHANGE_EVENT,
    #     group_callback["longRunningCommandsInQueue"],
    # )
    # group_callback["longRunningCommandsInQueue"].assert_change_event(
    #     (),
    # )
    result, unique_id = sdpmln_node.On()
    logger.info(result)
    logger.info(unique_id)
    # group_callback["longRunningCommandsInQueue"].assert_change_event(
    #     ("On",),
    # )
    logger.info(f"Command ID: {unique_id} Returned result: {result}")
    assert result[0] == ResultCode.QUEUED
    lrcr_id = sdpmln_node.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    logger.info(f"type unique_id[0]:{type(unique_id[0])}")
    logger.info(f"type str([ResultCode.OK:{type(ResultCode.OK.value)}")
    group_callback["longRunningCommandResult"].assert_change_event(
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=2,
    )

    # group_callback["longRunningCommandsInQueue"].assert_change_event(
    #     (),
    #     lookahead=2,
    # )
    # sdpmln_node.unsubscribe_event(lrcq_id)
    sdpmln_node.unsubscribe_event(lrcr_id)
    # Tear Down
    sdpmln_node.Off()


@pytest.mark.post_deployment
@pytest.mark.SKA_mid
def test_on_command_mid(tango_context, group_callback):
    on_command(tango_context, SDP_MASTER_LEAF_DEVICE_MID, group_callback)


@pytest.mark.post_deployment
@pytest.mark.SKA_low
def test_on_command_low(tango_context, group_callback):
    on_command(tango_context, SDP_MASTER_LEAF_DEVICE_LOW, group_callback)
