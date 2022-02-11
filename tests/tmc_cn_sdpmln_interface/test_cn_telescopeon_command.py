# WIP: This integration test is for verifying interface between TMC CentralNode and SdpMasterLeafNode device.
# This test can be updated as per requirement.
import time
from tango import DeviceProxy
import pytest
import logging

LOGGER = logging.getLogger(__name__)


@pytest.mark.tmcintegration
def test_cn_telescopeon():
    try:
        fixture = {}
        fixture["state"] = "Unknown"

        # given a started up telescope
        LOGGER.info("Staring up the Telescope")
        sdp_master = DeviceProxy("mid_sdp/elt/master")
        LOGGER.info(
        "Before Sending TelescopeOn command on sdp master state :"
        + str(sdp_master.State()))

        CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
        LOGGER.info(
        "Before Sending TelescopeOn command on CentralNode state :"
        + str(CentralNode.State())
        )
        # command invokation
        CentralNode.TelescopeOn()

        fixture["state"] = "Telescope On"
        LOGGER.info("Invoked TelescopeOn on CentralNode")

        time.sleep(10)
        LOGGER.info(
        "After Sending TelescopeOn command on sdp master state :"
        + str(sdp_master.State()))

        # command invokation
        CentralNode.TelescopeOff()
        fixture["state"] = "Telescope Off"

        time.sleep(10)
        LOGGER.info(
        "After Sending TelescopeOff command off CentralNode state :"
        + str(CentralNode.State())
        )
        LOGGER.info(
        "After Sending TelescopeOff command off sdp master state :"
        + str(sdp_master.State()))

        # tear down
        LOGGER.info("Tests complete: tearing down...")

    except:
        pytest.fail("unable to complete test without exceptions")

