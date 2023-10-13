"""Common Settings for testing of SDP Leaf Node"""
import logging
import time
from typing import List

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


def count_faulty_devices(cm):
    """Count faulty devices"""
    result = 0
    for dev_info in cm.checked_devices:
        if dev_info.unresponsive:
            result += 1
    return result


def create_cm(cm_class, device):
    """Create Component Manager"""
    if cm_class == "SdpMLNComponentManager":
        cm = SdpMLNComponentManager(
            device,
            logger=logger,
        )
    if cm_class == "SdpSLNComponentManager":
        cm = SdpSLNComponentManager(
            device, logger=logger, _liveliness_probe=LivelinessProbeType.NONE
        )
    else:
        log_msg = f"Unknown component manager class {cm_class}"
        logger.error(log_msg)

    return cm


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


def wait_for_attribute_value(device: DeviceProxy, attribute_name: str) -> bool:
    """Waits for attribute value to change on the given device."""
    start_time = time.time()
    while device.read_attribute(attribute_name).value == "[]":
        time.sleep(0.5)
        if time.time() - start_time >= 10:
            return False
    return True
