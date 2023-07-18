import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.abort_command import Abort
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
)





DEVICE_OBSSTATE = [
    (SDP_SUBARRAY_DEVICE_LOW, ObsState.RESOURCING),
    (SDP_SUBARRAY_DEVICE_LOW, ObsState.IDLE),
    (SDP_SUBARRAY_DEVICE_LOW, ObsState.CONFIGURING),
    (SDP_SUBARRAY_DEVICE_LOW, ObsState.READY),
    (SDP_SUBARRAY_DEVICE_LOW, ObsState.SCANNING),
    (SDP_SUBARRAY_DEVICE_MID, ObsState.RESOURCING),
    (SDP_SUBARRAY_DEVICE_MID, ObsState.IDLE),
    (SDP_SUBARRAY_DEVICE_MID, ObsState.CONFIGURING),
    (SDP_SUBARRAY_DEVICE_MID, ObsState.READY),
    (SDP_SUBARRAY_DEVICE_MID, ObsState.SCANNING),
]

@pytest.mark.test1
@pytest.mark.sdpsln
@pytest.mark.parametrize("devices , obsstate", DEVICE_OBSSTATE)
def test_abort_command(tango_context, devices, obsstate):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)

    cm.update_device_obs_state(obsstate)
    cm.is_command_allowed("Abort")
    logger.info(f"Abort command is allowed in {obsstate}.")
    result_code, _ = cm.abort_command()
    assert result_code == ResultCode.OK


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_abort_command_fail_subarray(tango_context, devices):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    adapter_factory.get_or_create_adapter(
        devices,
        AdapterType.SUBARRAY,
        attrs={"Abort.side_effect": Exception},
    )
    cm.update_device_obs_state(ObsState.IDLE)
    abort_command = Abort(cm, logger=logger)
    abort_command.adapter_factory = adapter_factory
    result_code, _ = abort_command.do()
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_abort_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.EMPTY)
    with pytest.raises(InvalidObsStateError):
        cm.is_command_allowed("Abort")


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_abort_fail_check_allowed_with_device_unresponsive(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed("Abort")
