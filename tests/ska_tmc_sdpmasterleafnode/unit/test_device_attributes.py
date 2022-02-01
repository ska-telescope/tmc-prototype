import pytest
import tango
from ska_tango_base.control_model import ControlMode, SimulationMode, TestMode
from tango import DevState
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpmasterleafnode import release
from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node_mid import (
    SdpMasterLeafNodeMid,
)


@pytest.fixture
def sdpmln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(SdpMasterLeafNodeMid) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "SdpMasterLeafNodeMid"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


def test_attributes(sdplmn_device):
    assert sdplmn_device.State() == DevState.ON
    sdplmn_device.loggingTargets = ["console::cout"]
    assert "console::cout" in sdplmn_device.loggingTargets
    sdplmn_device.testMode = TestMode.NONE
    assert sdplmn_device.testMode == TestMode.NONE
    sdplmn_device.simulationMode = SimulationMode.FALSE
    assert sdplmn_device.testMode == SimulationMode.FALSE
    sdplmn_device.controlMode = ControlMode.REMOTE
    assert sdplmn_device.controlMode == ControlMode.REMOTE
    sdplmn_device.sdpMasterDevName = "sdpmln"
    assert sdplmn_device.sdpMasterDevName == "sdpmln"
    assert sdplmn_device.versionId == release.version
    assert sdplmn_device.buildState == (
        "{},{},{}".format(release.name, release.version, release.description)
    )
