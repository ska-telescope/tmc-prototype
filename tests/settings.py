import logging
import time

import mock
import pytest
from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpmasterleafnode.manager import SdpMLNComponentManager
from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 100

SDP_SUBARRAY_DEVICE = "mid_sdp/elt/subarray_1"


def count_faulty_devices(cm):
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm(cm_class, input_parameter, device):
    op_state_model = TMCOpStateModel(logger)
    if cm_class == "SdpMLNComponentManager":
        cm = SdpMLNComponentManager(
            device,
            op_state_model,
            logger=logger,
        )
        cm.get_device()
    elif cm_class == "SdpSLNComponentManager":
        cm = SdpSLNComponentManager(
            op_state_model, _input_parameter=input_parameter, logger=logger
        )
        cm.add_device(device)
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
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    cm.update_device_obs_state(SDP_SUBARRAY_DEVICE, obsstate_value)

    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    command_obj = command_class(cm, cm.op_state_model, adapter_factory, skuid)
    return cm, command_obj, adapter_factory


def get_sdpmln_command_obj(command_class, device):
    cm, _ = create_cm("SdpMLNComponentManager", None, device)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)
    cm._sdp_master_dev_name = device
    command_obj = command_class(cm, cm.op_state_model, adapter_factory, skuid)
    return cm, command_obj, adapter_factory
