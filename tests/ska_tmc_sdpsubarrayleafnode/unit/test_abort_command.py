import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import Abort
from tests.settings import create_cm, get_sdpsln_command_obj, logger


@pytest.mark.sdpsln
def test_abort_command(tango_context, sdp_subarray_device):
    logger.info("%s", tango_context)
    _, abort_command, adapter_factory = get_sdpsln_command_obj(
        Abort, ObsState.CONFIGURING
    )

    assert abort_command.check_allowed()
    (result_code, _) = abort_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_subarray_device)
    adapter.proxy.Abort.assert_called()


@pytest.mark.sdpsln
def test_abort_command_fail_subarray(tango_context, sdp_subarray_device):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", sdp_subarray_device)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in ObsReset command
    attrs = {"Abort.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        sdp_subarray_device, proxy=subarrayMock
    )

    abort_command = Abort(cm, cm.op_state_model, adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.CONFIGURING)
    assert abort_command.check_allowed()
    (result_code, message) = abort_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_subarray_device in message
    cm.get_device().obs_state == ObsState.ABORTED


@pytest.mark.sdpsln
def test_abort_command_fail_check_allowed_with_invalid_obsState(tango_context):
    logger.info("%s", tango_context)
    cm, abort_command, _ = get_sdpsln_command_obj(
        Abort, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(False)
    with pytest.raises(
        InvalidObsStateError,
    ):
        abort_command.check_allowed()


@pytest.mark.sdpsln
def test_abort_command_fail_check_allowed_with_device_unresponsive(
    tango_context,
):
    logger.info("%s", tango_context)
    cm, abort_command, _ = get_sdpsln_command_obj(
        Abort, obsstate_value=ObsState.EMPTY
    )
    cm.get_device().update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        abort_command.check_allowed()
