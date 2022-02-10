import time

import pytest
from ska_tmc_common.device_info import SubArrayDeviceInfo

# from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.settings import SDP_SUBARRAY_DEVICE, create_cm, logger


@pytest.mark.sdpsln
def test_sdpsa_working(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    dev_info = cm.get_device()
    assert dev_info.unresponsive is False

    elapsed_time = time.time() - start_time
    logger.info("checked %s device in %s", dev_info.dev_name, elapsed_time)
    assert isinstance(dev_info, SubArrayDeviceInfo)


# TODO: Fix test case
# @pytest.mark.sdpsln
# def test_all_devices_faulty(tango_context):
#     logger.info("%s", tango_context)
#     # input_parameter = SdpSLNInputParameter(None)
#     cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
#     num_faulty = count_faulty_devices(cm)

#     elapsed_time = time.time() - start_time
#     logger.info("checked %s devices in %s", num_faulty, elapsed_time)
#     cm.add_device(SDP_SUBARRAY_DEVICE)

#     for devInfo in cm.devices:
#         devInfo.update_unresponsive(True)
#         assert devInfo.unresponsive
#     if "subarray" in devInfo.dev_name.lower():
#         assert isinstance(devInfo, SubArrayDeviceInfo)
