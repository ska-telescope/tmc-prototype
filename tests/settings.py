"""Common Settings for testing of SDP Leaf Node"""
import json
import logging
import time
from typing import List

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common import FaultType
from ska_tmc_common.enum import LivelinessProbeType
from tango import DeviceProxy

from ska_tmc_sdpmasterleafnode.manager.component_manager import (
    SdpMLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 100

SDP_SUBARRAY_DEVICE_MID = "mid-sdp/subarray/01"
SDP_SUBARRAY_DEVICE_LOW = "low-sdp/subarray/01"
SDP_MASTER_DEVICE_MID = "mid-sdp/control/0"
SDP_MASTER_DEVICE_LOW = "low-sdp/control/0"
SDP_SUBARRAY_LEAF_NODE_MID = "ska_mid/tm_leaf_node/sdp_subarray01"
SDP_SUBARRAY_LEAF_NODE_LOW = "ska_low/tm_leaf_node/sdp_subarray01"
SDP_MASTER_LEAF_DEVICE_MID = "ska_mid/tm_leaf_node/sdp_master"
SDP_MASTER_LEAF_DEVICE_LOW = "ska_low/tm_leaf_node/sdp_master"

TIMEOUT_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.STUCK_IN_INTERMEDIATE_STATE,
        "error_message": "Command stuck in processing",
        "result": ResultCode.FAILED,
        "intermediate_state": ObsState.RESOURCING,
    }
)

ERROR_PROPAGATION_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.COMMAND_NOT_ALLOWED,
        "error_message": "Exception occured, command failed.",
        "result": ResultCode.FAILED,
    }
)

RESET_DEFECT = json.dumps(
    {
        "enabled": False,
        "fault_type": FaultType.FAILED_RESULT,
        "error_message": "Default exception.",
        "result": ResultCode.FAILED,
    }
)


def count_faulty_devices(component_manager):
    """Count faulty devices"""
    result = 0
    for dev_info in component_manager.checked_devices:
        if dev_info.unresponsive:
            result += 1
    return result


def create_cm(cm_class, device):
    """Create Component Manager"""
    component_manager = ""
    if cm_class == "SdpMLNComponentManager":
        component_manager = SdpMLNComponentManager(
            device,
            logger=logger,
        )
    if cm_class == "SdpSLNComponentManager":
        component_manager = SdpSLNComponentManager(
            device, logger=logger, _liveliness_probe=LivelinessProbeType.NONE
        )
    else:
        log_msg = f"Unknown component manager class {cm_class}"
        logger.error(log_msg)

    return component_manager


def event_remover(change_event_callbacks, attributes: List[str]) -> None:
    """Removes residual events from the queue."""
    for attribute in attributes:
        try:
            iterable = change_event_callbacks._mock_consumer_group._views[
                attribute
            ]._iterable
            for node in iterable:
                logger.info("Payload is: %s", repr(node.payload))
                node.drop()
        except KeyError:
            pass


def wait_for_attribute_value(
    device: DeviceProxy,
    attribute_name: str,
    attribute_value,
) -> bool:
    """Waits for attribute value to change on the given device."""
    start_time = time.time()
    while device.read_attribute(attribute_name).value == attribute_value:
        time.sleep(0.5)

        if time.time() - start_time >= 10:
            logger.info(
                "The attribute value after time out is: %s",
                device.read_attribute(attribute_name).value,
            )
            return False
    return True


def wait_for_cm_obstate_attribute_value(cm, obs_state: ObsState) -> bool:
    """Waits for attribute value to change on the given device."""
    start_time = time.time()
    while cm.get_obs_state() != obs_state:
        time.sleep(0.5)
        if time.time() - start_time >= 100:
            logger.info(
                "The attribute value after time out is: %s",
                cm.get_obs_state(),
            )
            return False
    return True
