import time

# import pytest
from ska_tmc_common.device_info import SubArrayDeviceInfo

from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.settings import count_faulty_devices, create_cm_parametrize, logger

SDP_SUBARRAY_DEVICE = "sdp_mid/elt/subarray_1"


def test_sdpsa_working(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    num_faulty = count_faulty_devices(cm)
    assert num_faulty == 0

    elapsed_time = time.time() - start_time
    logger.info("checked %s devices in %s", num_faulty, elapsed_time)
    for devInfo in cm.devices:
        assert not devInfo.unresponsive
    if "subarray" in devInfo.dev_name.lower():
        assert isinstance(devInfo, SubArrayDeviceInfo)


# Note: Sample implementation of test case that uses parametrized
# function to create component manager class object.
# @pytest.mark.sdpmln
# def test_sdpsa_working(tango_context):
#     logger.info("%s", tango_context)
#     input_parameter = SdpSLNInputParameter(None)
#     cm, start_time = create_cm_parametrize(
#         "SdpSLNComponentManager", input_parameter, "sdp_mid/elt/subarray_01"
#     )
#     num_faulty = count_faulty_devices(cm)
#     assert num_faulty == 0

#     elapsed_time = time.time() - start_time
#     logger.info("checked %s devices in %s", num_faulty, elapsed_time)
#     for devInfo in cm.devices:
#         assert not devInfo.unresponsive
#     if "subarray" in devInfo.dev_name.lower():
#         assert isinstance(devInfo, SubArrayDeviceInfo)
