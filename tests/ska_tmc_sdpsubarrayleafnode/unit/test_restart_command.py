import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.restart_command import Restart
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    DeviceUnresponsive,
    InvalidObsStateError,
)

# from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_restart_command(tango_context):
    logger.info("%s", tango_context)
    cm, restart_command, my_adapter_factory = get_sdpsln_command_obj(
        Restart, obsstate_value=ObsState.ABORTED
    )
    assert restart_command.check_allowed()
    (result_code, _) = restart_command.do()
    assert result_code == ResultCode.OK
    # dev_name = "mid_sdp/elt/subarray_1"
    cm.get_device().obsState == ObsState.EMPTY
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Restart.assert_called()


@pytest.mark.sdpsln
def test_telescope_restart_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    # input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in ObsReset command
    # failing_dev = "mid_sdp/elt/subarray_1"
    attrs = {"Restart.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, proxy=subarrayMock
    )

    restart_command = Restart(cm, cm.op_state_model, my_adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.ABORTED)
    assert restart_command.check_allowed()
    (result_code, message) = restart_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.sdpsln
def test_telescope_restart_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, restart_command, _ = get_sdpsln_command_obj(
        Restart, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(InvalidObsStateError):
        restart_command.check_allowed()


@pytest.mark.sdpsln
def test_telescope_restart_fail_check_allowed_with_device_undesponsive(
    tango_context,
):

    logger.info("%s", tango_context)
    cm, restart_command, _ = get_sdpsln_command_obj(
        Restart, obsstate_value=ObsState.ABORTED
    )
    device_info = cm.get_device()
    device_info.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        restart_command.check_allowed()
