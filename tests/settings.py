"""Common Settings for testing of SDP Leaf Node"""
import logging
import time

import mock
from ska_tmc_common.op_state_model import TMCOpStateModel
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


def count_faulty_devices(cm):
    """Count faulty devices"""
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm(cm_class, device):
    """Create Component Manager"""
    op_state_model = TMCOpStateModel(logger)
    if cm_class == "SdpMLNComponentManager":
        cm = SdpMLNComponentManager(
            device,
            op_state_model,
            logger=logger,
        )
    elif cm_class == "SdpSLNComponentManager":
        cm = SdpSLNComponentManager(device, op_state_model, logger=logger)
    else:
        log_msg = f"Unknown component manager class {cm_class}"
        logger.error(log_msg)

    return cm


def get_sdpsln_command_obj(
    command_class,
    devices,
    obsstate_value=None,
):
    """Returns component manager and command class object for Sdp
    Subarray Leaf Node"""
    cm, start_time = create_cm("SdpSLNComponentManager", devices)
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
    adapter_factory = HelperAdapterFactory()
    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)
    cm.sdp_master_dev_name = devices
    command_obj = command_class(cm, cm.op_state_model, adapter_factory, skuid)
    return cm, command_obj, adapter_factory
