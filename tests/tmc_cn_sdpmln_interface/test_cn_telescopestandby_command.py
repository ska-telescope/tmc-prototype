# WIP: This integration test is for verifying interface between TMC CentralNode and SdpMasterLeafNode device.
# This test can be updated as per requirement.
import logging
import time

import pytest
from tango import DeviceProxy, DevState

LOGGER = logging.getLogger(__name__)


@pytest.mark.xfail
def test_cn_telescopestandby():
    try:
        fixture = {}
        fixture["state"] = "Unknown"

        # given a started up telescope
        LOGGER.info("Staring up the Telescope")

        CentralNode = DeviceProxy("ska_mid/tm_central/central_node")
        sdp_mln = DeviceProxy("ska_mid/tm_leaf_node/sdp_master")
        sdp_master = DeviceProxy("mid_sdp/elt/master")

        assert CentralNode.State() == DevState.ON
        assert CentralNode.telescopeState == DevState.UNKNOWN
        assert sdp_mln.State() == DevState.ON

        # command invokation
        CentralNode.TelescopeOn()

        fixture["state"] = "Telescope On"
        LOGGER.info("Invoked TelescopeOn on CentralNode")

        time.sleep(10)
        assert CentralNode.State() == DevState.ON
        assert CentralNode.telescopeState == DevState.UNKNOWN
        assert sdp_mln.State() == DevState.ON
        assert sdp_master.State() == DevState.ON

        # command invokation
        CentralNode.TelescopeStandby()
        fixture["state"] = "Telescope standby"

        time.sleep(10)
        assert CentralNode.State() == DevState.ON
        assert CentralNode.telescopeState == DevState.UNKNOWN
        assert sdp_mln.State() == DevState.ON
        assert sdp_master.State() == DevState.STANDBY

        LOGGER.info("Tests complete: tearing down...")
    except Exception:
        LOGGER.info(
            "Tearing down failed test, state = {}".format(fixture["state"])
        )
        if fixture["state"] == "Telescope On":
            CentralNode.TelescopeOff()
        pytest.fail("unable to complete test without exceptions")
