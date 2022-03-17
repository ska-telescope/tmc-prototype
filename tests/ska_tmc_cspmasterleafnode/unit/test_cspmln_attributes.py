import pytest
import tango
from ska_tango_base.control_model import ControlMode, SimulationMode, TestMode
from tango import DevState
from tango.test_utils import DeviceTestContext

from ska_tmc_cspmasterleafnode import release
from ska_tmc_cspmasterleafnode.csp_master_leaf_node import CspMasterLeafNode


@pytest.fixture
def cspmln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(CspMasterLeafNode) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "CspMasterLeafNode"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.mark.cspmln
def test_attributes(cspmln_device):
    assert cspmln_device.State() == DevState.ON
    cspmln_device.loggingTargets = ["console::cout"]
    assert "console::cout" in cspmln_device.loggingTargets
    cspmln_device.testMode = TestMode.NONE
    assert cspmln_device.testMode == TestMode.NONE
    cspmln_device.simulationMode = SimulationMode.FALSE
    assert cspmln_device.testMode == SimulationMode.FALSE
    cspmln_device.controlMode = ControlMode.REMOTE
    assert cspmln_device.controlMode == ControlMode.REMOTE
    assert len(cspmln_device.commandExecuted) == 1  # init
    cspmln_device.cspMasterDevName = "cspmln"
    assert cspmln_device.cspMasterDevName == "cspmln"
    assert cspmln_device.versionId == release.version
    assert cspmln_device.buildState == (
        "{},{},{}".format(release.name, release.version, release.description)
    )
