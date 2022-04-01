import logging
import time

import mock
import pytest
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

SDP_SUBARRAY_DEVICE = "mid_sdp/elt/subarray_1"
SDP_MASTER_DEVICE = "mid_sdp/elt/master"


def count_faulty_devices(cm):
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm(cm_class, device):
    op_state_model = TMCOpStateModel(logger)
    if cm_class == "SdpMLNComponentManager":
        cm = SdpMLNComponentManager(
            device,
            op_state_model,
            logger=logger,
        )
        cm.get_device()
    elif cm_class == "SdpSLNComponentManager":
        cm = SdpSLNComponentManager(device, op_state_model, logger=logger)
    else:
        log_msg = f"Unknown component manager class {cm_class}"
        logger.error(log_msg)

    start_time = time.time()
    time.sleep(SLEEP_TIME)
    elapsed_time = time.time() - start_time
    if elapsed_time > TIMEOUT:
        pytest.fail("Timeout occurred while executing the test")

    return cm, start_time


def get_sdpsln_command_obj(command_class, obsstate_value=None):
    """Returns component manager and command class object for Sdp Subarray Leaf Node"""
    cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
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


def get_sdpmln_command_obj(command_class):
    """Returns component manager and command class object for Sdp Master Leaf Node"""
    cm, start_time = create_cm("SdpMLNComponentManager", SDP_MASTER_DEVICE)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)
    cm._sdp_master_dev_name = SDP_MASTER_DEVICE
    command_obj = command_class(cm, cm.op_state_model, adapter_factory, skuid)
    return cm, command_obj, adapter_factory
