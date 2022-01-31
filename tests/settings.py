import logging
import time

import pytest
from ska_tmc_common.op_state_model import TMCOpStateModel

from ska_tmc_sdpmasterleafnode.manager.component_manager import (
    SdpMLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 100

DEVICE_MID = "mid_sdp/elt/subarray_1"


def count_faulty_devices(cm):
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm_parametrize(cm_class, input_parameter, device):
    op_state_model = TMCOpStateModel(logger)
    if cm_class == "SdpMLNComponentManager":
        cm = SdpMLNComponentManager(
            op_state_model,
            _input_parameter=input_parameter,
            logger=logger,
        )
    elif cm_class == "SdpSLNComponentManager":
        cm = SdpSLNComponentManager(
            op_state_model, _input_parameter=input_parameter, logger=logger
        )
    else:
        log_msg = f"Unknown component manager class {cm_class}"
        logger.error(log_msg)

    cm.add_device(device)
    start_time = time.time()
    time.sleep(SLEEP_TIME)
    elapsed_time = time.time() - start_time
    if elapsed_time > TIMEOUT:
        pytest.fail("Timeout occurred while executing the test")

    return cm, start_time
