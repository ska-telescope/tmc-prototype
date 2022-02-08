import pytest

from tests.settings import create_cm, logger

SDP_MASTER_DEVICE = "mid_sdp/elt/master"


@pytest.mark.sdpmln
def test_sdpmaster_working(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, SDP_MASTER_DEVICE)
    devInfo = cm.get_device()
    assert not devInfo.unresponsive


@pytest.mark.sdpmln
def test_sdp_master_unresponsive(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpMLNComponentManager", None, SDP_MASTER_DEVICE)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    assert devInfo.unresponsive
