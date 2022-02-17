import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import End
from tests.settings import create_cm, get_sdpsln_command_obj, logger


@pytest.mark.sdpsln
def test_telescope_end_command(tango_context, sdp_subarray_device):
    logger.info("%s", tango_context)
    _, end_command, adapter_factory = get_sdpsln_command_obj(
        End, obsstate_value=ObsState.READY
    )

    assert end_command.check_allowed()
    (result_code, _) = end_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_subarray_device)
    adapter.proxy.End.assert_called()


@pytest.mark.sdpsln
def test_telescope_assign_resources_command_fail_subarray(
    tango_context, sdp_subarray_device
):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", sdp_subarray_device)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )

    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    attrs = {"End.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        sdp_subarray_device, proxy=subarrayMock
    )

    end_command = End(cm, cm.op_state_model, adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.READY)
    assert end_command.check_allowed()
    (result_code, message) = end_command.do()
    assert result_code == ResultCode.FAILED
    assert sdp_subarray_device in message


@pytest.mark.sdpsln
def test_telescope_end_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):
    logger.info("%s", tango_context)
    _, end_command, _ = get_sdpsln_command_obj(
        End, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(
        InvalidObsStateError,
        match="Scan and End commands are not allowed in current observation state",
    ):
        end_command.check_allowed()
