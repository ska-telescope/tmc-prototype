import time

import pytest
from ska_tmc_common.device_info import DeviceInfo

from tests.settings import create_cm, logger


@pytest.mark.sdpsln
def test_sdpsa_working(tango_context, devices):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", devices)
    dev_info = cm.get_device()
    assert dev_info.unresponsive is False

    elapsed_time = time.time() - start_time
    logger.info("checked %s device in %s", dev_info.dev_name, elapsed_time)
    assert isinstance(dev_info, DeviceInfo)


@pytest.mark.sdpsln
def test_sdpsa_faulty(tango_context, devices):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", devices)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    assert devInfo.unresponsive
