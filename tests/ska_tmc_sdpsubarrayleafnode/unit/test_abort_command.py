import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from ska_tmc_sdpsubarrayleafnode.commands.abort_command import Abort
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    DeviceUnresponsive,
    InvalidObsStateError,
)
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_abort_command(tango_context):
    logger.info("%s", tango_context)
    _, abort_command, my_adapter_factory = get_sdpsln_command_obj(
        Abort, ObsState.CONFIGURING
    )

    assert abort_command.check_allowed()
    (result_code, _) = abort_command.do()
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.Abort.assert_called()


@pytest.mark.sdpsln
def test_telescope_abort_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, _ = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in ObsReset command
    attrs = {"Abort.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, proxy=subarrayMock
    )

    abort_command = Abort(cm, cm.op_state_model, adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.CONFIGURING)
    assert abort_command.check_allowed()
    (result_code, message) = abort_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message
    cm.get_device().obsState == ObsState.ABORTED


@pytest.mark.sdpsln
def test_telescope_abort_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, abort_command, _ = get_sdpsln_command_obj(Abort, ObsState.ABORTED)
    with pytest.raises(InvalidObsStateError):
        abort_command.check_allowed()


@pytest.mark.sdpsln
def test_telescope_abort_command_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, abort_command, _ = get_sdpsln_command_obj(Abort, ObsState.ABORTED)
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        abort_command.check_allowed()
