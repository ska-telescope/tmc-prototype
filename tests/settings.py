"""Common Settings for testing of SDP Leaf Node"""
import logging
import time
from typing import List

import mock
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

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
SDP_MASTER_LEAF_DEVICE_MID = "ska_mid/tm_leaf_node/sdp_master"
SDP_MASTER_LEAF_DEVICE_LOW = "ska_low/tm_leaf_node/sdp_master"


def count_faulty_devices(cm):
    """Count faulty devices"""
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm(cm_class, device):
    """Create Component Manager"""
    adapter_factory = HelperAdapterFactory()
    if cm_class == "SdpMLNComponentManager":
        cm = SdpMLNComponentManager(
            device,
            logger,
            _liveliness_probe=LivelinessProbeType.NONE,
        )
    elif cm_class == "SdpSLNComponentManager":
        cm = SdpSLNComponentManager(
            device,
            adapter_factory,
            logger,
            _liveliness_probe=LivelinessProbeType.NONE,
        )
    else:
        log_msg = f"Unknown component manager class {cm_class}"
        logger.error(log_msg)

    start_time = time.time()
    return cm, start_time


def get_sdpsln_command_obj(
    command_class,
    devices,
    obsstate_value=None,
):
    """Returns component manager and command class object for Sdp
    Subarray Leaf Node"""
    cm, start_time = create_cm("SdpSLNComponentManager", devices)
    cm.stop_liveliness_probe()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )
    cm.update_device_obs_state(obsstate_value)

    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    command_obj = command_class(cm, cm.op_state_model, adapter_factory, skuid)
    return cm, command_obj, adapter_factory


def get_sdpmln_command_obj(command_class, devices):
    """Returns component manager and command class object for Sdp Master Leaf
    Node"""
    cm, _ = create_cm("SdpMLNComponentManager", devices)
    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)
    cm.sdp_master_device_name = devices
    command_obj = command_class(cm, skuid)
    return cm, command_obj


def event_remover(group_callback, attributes: List[str]) -> None:
    """Removes residual events from the queue."""
    for attribute in attributes:
        try:
            iterable = group_callback._mock_consumer_group._views[
                attribute
            ]._iterable
            for node in iterable:
                logger.info("Payload is: %s", repr(node.payload))
                node.drop()
        except KeyError:
            pass
