import pytest

from tests.settings import create_cm, logger


@pytest.mark.sdpmln
def test_sdpmaster_working(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, sdp_master_device)
    dev_info = cm.get_device()
    assert not dev_info.unresponsive


@pytest.mark.sdpmln
def test_sdp_master_unresponsive(tango_context, sdp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, sdp_master_device)
    dev_info = cm.get_device()
    dev_info.update_unresponsive(True)
    assert dev_info.unresponsive
