import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError

from ska_tmc_sdpsubarrayleafnode.commands.endscan_command import EndScan
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_endscan_command(tango_context):
    logger.info("%s", tango_context)
    cm, endscan_command, my_adapter_factory = get_sdpsln_command_obj(
        EndScan, obsstate_value=ObsState.SCANNING
    )
    assert endscan_command.check_allowed()
    (result_code, _) = endscan_command.do("")
    assert result_code == ResultCode.OK
    cm.get_device().obsState == ObsState.READY
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.EndScan.assert_called()


@pytest.mark.sdpsln
def test_endscan_fail_check_allowed_with_device_unresponsive(tango_context):

    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )
    adapter_factory = HelperAdapterFactory()
    cm.get_device().update_unresponsive(True)
    endscan_command = EndScan(cm, cm.op_state_model, adapter_factory)
    with pytest.raises(DeviceUnresponsive):
        endscan_command.check_allowed()


@pytest.mark.sdpsln
def test_endscan_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, endscan_command, _ = get_sdpsln_command_obj(
        EndScan, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(InvalidObsStateError):
        endscan_command.check_allowed()
