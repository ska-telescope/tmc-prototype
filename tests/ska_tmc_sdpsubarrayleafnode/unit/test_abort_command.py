import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import Abort
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)

device_obsstate = []
devices = [SDP_SUBARRAY_DEVICE_LOW, SDP_SUBARRAY_DEVICE_MID]
obsstates = [
    ObsState.RESOURCING,
    ObsState.IDLE,
    ObsState.CONFIGURING,
    ObsState.READY,
    ObsState.SCANNING,
]
for device in devices:
    for obsstate in obsstates:
        device_obsstate.append((device, obsstate))


@pytest.mark.sdpsln
@pytest.mark.parametrize("devices ,obsstate", device_obsstate)
def test_abort_command(tango_context, devices, obsstate):
    logger.info("%s", tango_context)
    _, abort_command, adapter_factory = get_sdpsln_command_obj(
        Abort, devices, obsstate
    )

    assert abort_command.check_allowed()
    (result_code, _) = abort_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(devices)
    adapter.proxy.Abort.assert_called_once_with()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_abort_command_fail_subarray(tango_context, devices):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in ObsReset command
    attrs = {"Abort.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(devices, proxy=subarrayMock)

    abort_command = Abort(cm, cm.op_state_model, adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.CONFIGURING)
    assert abort_command.check_allowed()
    (result_code, message) = abort_command.do()
    assert result_code == ResultCode.FAILED
    assert devices in message
    cm.get_device().obs_state == ObsState.ABORTED


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_abort_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, abort_command, _ = get_sdpsln_command_obj(
        Abort, devices, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(False)
    with pytest.raises(
        InvalidObsStateError,
    ):
        abort_command.check_allowed()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_abort_command_fail_check_allowed_with_device_unresponsive(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm, abort_command, _ = get_sdpsln_command_obj(
        Abort, devices, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        abort_command.check_allowed()
