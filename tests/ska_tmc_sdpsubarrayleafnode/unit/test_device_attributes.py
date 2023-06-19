import pytest
from ska_tango_base.control_model import (
    ControlMode,
    ObsState,
    SimulationMode,
    TestMode,
)
from tango import DevState

from ska_tmc_sdpsubarrayleafnode import release


@pytest.mark.sdpsln
def test_attributes(sdpsln_device):
    assert sdpsln_device.State() == DevState.ON
    sdpsln_device.loggingTargets = ["console::cout"]
    assert "console::cout" in sdpsln_device.loggingTargets
    obs_state = ObsState.EMPTY
    assert sdpsln_device.State() == obs_state
    # Negative test case
    invalid_obs_state = ObsState.IDLE
    assert sdpsln_device.State() != invalid_obs_state

    # Ensure the state remains unchanged after negative scenario
    assert sdpsln_device.State() == obs_state
    sdpsln_device.testMode = TestMode.NONE
    assert sdpsln_device.testMode == TestMode.NONE
    sdpsln_device.simulationMode = SimulationMode.FALSE
    assert sdpsln_device.testMode == SimulationMode.FALSE
    sdpsln_device.controlMode = ControlMode.REMOTE
    assert sdpsln_device.controlMode == ControlMode.REMOTE
    sdpsln_device.sdpSubarrayDevName = "sdpsa"
    assert sdpsln_device.sdpSubarrayDevName == "sdpsa"
    assert sdpsln_device.versionId == release.version
    assert sdpsln_device.buildState == (
        "{},{},{}".format(release.name, release.version, release.description)
    )
