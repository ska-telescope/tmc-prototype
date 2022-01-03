import logging
import time

import pytest

from ska_tmc_sdpsubarrayleafnode.manager.component_manager import (
    SdpSLNComponentManager,
)
from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid
from ska_tmc_sdpsubarrayleafnode.model.op_state_model import TMCOpStateModel

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 10

DEVICE_LIST_MID = [
    "mid_sdp/elt/subarray_01",
]


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
        DEVICE_LIST = DEVICE_LIST_MID

    for dev in DEVICE_LIST:
        cm.add_device(dev)
    start_time = time.time()
    num_devices = len(DEVICE_LIST)
    while num_devices != len(cm.checked_devices):
        time.sleep(SLEEP_TIME)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")

    return cm, start_time


# def create_cm_no_faulty_devices(
#     tango_context,
#     input_parameter=InputParameterMid(None),
# ):
#     logger.info("%s", tango_context)
#     if isinstance(input_parameter, InputParameterMid):
#         input_parameter = InputParameterMid(None)
#     else:
#         input_parameter = InputParameterLow(None)

#     cm, start_time = create_cm(
#         p_monitoring_loop, p_event_receiver, input_parameter
#     )
#     num_faulty = count_faulty_devices(cm)
#     assert num_faulty == 0
#     elapsed_time = time.time() - start_time
#     logger.info("checked %s devices in %s", num_faulty, elapsed_time)
#     return cm


# def ensure_telescope_state(cm, state, expected_elapsed_time):
#     start_time = time.time()
#     elapsed_time = 0
#     while cm.component.telescope_state != state:
#         elapsed_time = time.time() - start_time
#         time.sleep(0.1)
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")
#     assert elapsed_time < expected_elapsed_time


# def ensure_tmc_op_state(cm, state, expected_elapsed_time):
#     start_time = time.time()
#     elapsed_time = 0
#     while cm.component.tmc_op_state != state:
#         elapsed_time = time.time() - start_time
#         time.sleep(0.1)
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")
#     assert elapsed_time < expected_elapsed_time


# def ensure_imaging(cm, value, expected_elapsed_time):
#     start_time = time.time()
#     elapsed_time = 0
#     while cm.component.imaging != value:
#         elapsed_time = time.time() - start_time
#         time.sleep(0.1)
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")
#     assert elapsed_time < expected_elapsed_time


# def set_devices_state(devices, state, devFactory, cm, expected_elapsed_time):
#     for device in devices:
#         proxy = devFactory.get_device(device)
#         proxy.SetDirectState(state)
#         assert proxy.State() == state


# def set_device_state(device, state, devFactory):
#     proxy = devFactory.get_device(device)
#     proxy.SetDirectState(state)
#     assert proxy.State() == state
