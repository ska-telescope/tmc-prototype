import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import ObsReset
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_obsreset_command(tango_context):
    logger.info("%s", tango_context)
    cm, obsreset_command, adapter_factory = get_sdpsln_command_obj(
        ObsReset, obsstate_value=ObsState.ABORTED
    )
    assert obsreset_command.check_allowed()
    (result_code, _) = obsreset_command.do()
    assert result_code == ResultCode.OK
    cm.get_device().obsState == ObsState.IDLE
    adapter = adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    adapter.proxy.ObsReset.assert_called()


@pytest.mark.sdpsln
def test_telescope_obsreset_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", cm.get_device().dev_name, elapsed_time
    )

    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in ObsReset command
    attrs = {"ObsReset.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, proxy=subarrayMock
    )

    obsreset_command = ObsReset(cm, cm.op_state_model, adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.ABORTED)
    assert obsreset_command.check_allowed()
    (result_code, message) = obsreset_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.sdpsln
def test_telescope_obsreset_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, obsreset_command, _ = get_sdpsln_command_obj(
        ObsReset, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(InvalidObsStateError):
        obsreset_command.check_allowed()


@pytest.mark.sdpsln
def test_telescope_obsreset_fail_check_allowed_with_device_unresponsive(
    tango_context,
):

    logger.info("%s", tango_context)
    cm, obsreset_command, my_adapter_factory = get_sdpsln_command_obj(
        ObsReset, obsstate_value=ObsState.IDLE
    )
    cm.get_device().update_unresponsive((True))
    obsreset_command = ObsReset(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(DeviceUnresponsive):
        obsreset_command.check_allowed()
