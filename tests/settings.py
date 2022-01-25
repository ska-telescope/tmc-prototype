import logging
import time

import pytest
from ska_tmc_common.op_state_model import TMCOpStateModel

from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 100

DEVICE_MID = "mid_sdp/elt/subarray_01"


def count_faulty_devices(cm):
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm(
    input_parameter=InputParameterMid(None),
):
    op_state_model = TMCOpStateModel(logger)
    cm = SdpSLNComponentManager(
        op_state_model,
        logger=logger,
        _input_parameter=input_parameter,
    )

    if isinstance(input_parameter, InputParameterMid):
        DEVICE = DEVICE_MID

    cm.add_device(DEVICE)
    start_time = time.time()
    time.sleep(SLEEP_TIME)
    elapsed_time = time.time() - start_time
    if elapsed_time > TIMEOUT:
        pytest.fail("Timeout occurred while executing the test")

    return cm, start_time


def create_cm_no_faulty_devices(
    tango_context,
    input_parameter=InputParameterMid(None),
):
    logger.info("%s", tango_context)
    if isinstance(input_parameter, InputParameterMid):
        input_parameter = InputParameterMid(None)

    cm, start_time = create_cm(input_parameter)
    num_faulty = count_faulty_devices(cm)
    assert num_faulty == 0
    elapsed_time = time.time() - start_time
    logger.info("checked %s devices in %s", num_faulty, elapsed_time)
    return cm
