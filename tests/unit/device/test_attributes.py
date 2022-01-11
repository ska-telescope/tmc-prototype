import json

import pytest
import tango
from ska_tango_base.control_model import (
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)
from tango import DevState
from tango.test_utils import DeviceTestContext

from ska_tmc_sdpsubarrayleafnode import release
from ska_tmc_sdpsubarrayleafnode.sdp_subarray_leaf_node_mid import (
    SdpSubarrayLeafNodeMid,
)


@pytest.fixture
def sdpsln_device(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(SdpSubarrayLeafNodeMid) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "SdpSubarrayLeafNodeMid"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.mark.shraddha
def test_attributes(sdpsln_device):
    assert sdpsln_device.State() == DevState.ON
    sdpsln_device.loggingTargets = ["console::cout"]
    assert "console::cout" in sdpsln_device.loggingTargets
    sdpsln_device.testMode = TestMode.NONE
    assert sdpsln_device.testMode == TestMode.NONE
    sdpsln_device.simulationMode = SimulationMode.FALSE
    assert sdpsln_device.testMode == SimulationMode.FALSE
    sdpsln_device.controlMode = ControlMode.REMOTE
    assert sdpsln_device.controlMode == ControlMode.REMOTE
    sdpsln_device.sdpSubarrayDevName = "sdpSubarray"
    assert sdpsln_device.sdpSubarrayDevName == "sdpSubarray"
    assert sdpsln_device.versionId == release.version
    assert sdpsln_device.buildState == (
        "{},{},{}".format(release.name, release.version, release.description)
    )
