import time

import pytest
from ska_tmc_common.device_info import SubArrayDeviceInfo

from ska_tmc_sdpsubarrayleafnode.model.input import InputParameterMid
from tests.settings import (
    DEVICE_MID,
    count_faulty_devices,
    create_cm_parametrize,
    logger,
)

# def test_all_devices_faulty(tango_context):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm()
#     num_faulty = count_faulty_devices(cm)

#     elapsed_time = time.time() - start_time
#     logger.info("checked %s devices in %s", num_faulty, elapsed_time)
#     cm.add_device(DEVICE_MID)

#     for devInfo in cm.devices:
#         devInfo.update_unresponsive(True)
#         assert devInfo.unresponsive
#     if "subarray" in devInfo.dev_name.lower():
#         assert isinstance(devInfo, SubArrayDeviceInfo)


@pytest.mark.sdpsln
def test_all_devices_faulty(tango_context):
    logger.info("%s", tango_context)
    input_parameter = InputParameterMid(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, "sdp_mid/elt/subarray_01"
    )
    num_faulty = count_faulty_devices(cm)

    elapsed_time = time.time() - start_time
    logger.info("checked %s devices in %s", num_faulty, elapsed_time)
    cm.add_device(DEVICE_MID)

    for devInfo in cm.devices:
        devInfo.update_unresponsive(True)
        assert devInfo.unresponsive
    if "subarray" in devInfo.dev_name.lower():
        assert isinstance(devInfo, SubArrayDeviceInfo)
