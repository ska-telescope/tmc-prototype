import time

import pytest

from ska_tmc_sdpmasterleafnode.model.input import SdpMLNInputParameter
from tests.settings import count_faulty_devices, create_cm, logger

SDP_MASTER_DEVICE = "mid_sdp/elt/master"


@pytest.mark.sdpmln
def test_sdpmaster_working(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpMLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpMLNComponentManager", input_parameter, SDP_MASTER_DEVICE
    )
    num_faulty = count_faulty_devices(cm)
    assert num_faulty == 0

    elapsed_time = time.time() - start_time
    logger.info("checked %s devices in %s", num_faulty, elapsed_time)
    for devInfo in cm.devices:
        assert not devInfo.unresponsive


@pytest.mark.sdpmln
def test_sdp_master_unresponsive(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpMLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpMLNComponentManager", input_parameter, SDP_MASTER_DEVICE
    )
    num_faulty = count_faulty_devices(cm)

    elapsed_time = time.time() - start_time
    logger.info("checked %s devices in %s", num_faulty, elapsed_time)

    for devInfo in cm.devices:
        devInfo.update_unresponsive(True)
        assert devInfo.unresponsive


# TODO: This test case should be implemented in better way.
# Currently it does not add much value apart from marginally increasing code coverage
@pytest.mark.sdpmln
def test_sdpmln_input_parameter_update(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpMLNInputParameter(None)
    assert input_parameter.sdp_master_dev_name == "mid_sdp/elt/master"

    cm, start_time = create_cm(
        "SdpMLNComponentManager", input_parameter, SDP_MASTER_DEVICE
    )
    num_faulty = count_faulty_devices(cm)

    elapsed_time = time.time() - start_time
    logger.info("checked %s devices in %s", num_faulty, elapsed_time)

    cm.update_input_parameter()

    assert input_parameter.sdp_master_dev_name == "mid_sdp/elt/master"