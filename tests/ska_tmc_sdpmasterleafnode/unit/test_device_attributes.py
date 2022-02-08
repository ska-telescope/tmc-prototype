import pytest
import tango
from ska_tango_base.control_model import ControlMode, SimulationMode, TestMode
from tango import DevState
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpmasterleafnode import release
from ska_tmc_sdpmasterleafnode.sdp_master_leaf_node import SdpMasterLeafNode


@pytest.fixture
def sdpmln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(SdpMasterLeafNode) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "SdpMasterLeafNode"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.mark.verify
def test_attributes(sdpmln_device):
    assert sdpmln_device.State() == DevState.ON
    sdpmln_device.loggingTargets = ["console::cout"]
    assert "console::cout" in sdpmln_device.loggingTargets
    sdpmln_device.testMode = TestMode.NONE
    assert sdpmln_device.testMode == TestMode.NONE
    sdpmln_device.simulationMode = SimulationMode.FALSE
    assert sdpmln_device.testMode == SimulationMode.FALSE
    sdpmln_device.controlMode = ControlMode.REMOTE
    assert sdpmln_device.controlMode == ControlMode.REMOTE
    sdpmln_device.sdpMasterDevName = "sdpmln"
    assert sdpmln_device.sdpMasterDevName == "sdpmln"
    assert sdpmln_device.versionId == release.version
    assert sdpmln_device.buildState == (
        "{},{},{}".format(release.name, release.version, release.description)
    )
