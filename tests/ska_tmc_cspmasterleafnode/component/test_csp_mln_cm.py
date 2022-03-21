import pytest

from tests.settings import create_cm, logger


@pytest.mark.cspmln
def test_cspmaster_working(tango_context, csp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("CspMLNComponentManager", csp_master_device)
    dev_info = cm.get_device()
    assert not dev_info.unresponsive


@pytest.mark.cspmln
def test_csp_master_unresponsive(tango_context, csp_master_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("CspMLNComponentManager", csp_master_device)
    dev_info = cm.get_device()
    dev_info.update_unresponsive(True)
    assert dev_info.unresponsive
