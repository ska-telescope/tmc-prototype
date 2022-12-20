import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import EndScan
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_endscan_command(tango_context, devices):
    logger.info("%s", tango_context)
    cm, endscan_command, adapter_factory = get_sdpsln_command_obj(
        EndScan, devices, obsstate_value=ObsState.SCANNING
    )
    assert endscan_command.check_allowed()
    (result_code, _) = endscan_command.do("")
    assert result_code == ResultCode.OK
    cm.get_device().obs_state == ObsState.READY
    adapter = adapter_factory.get_or_create_adapter(devices)
    adapter.proxy.EndScan.assert_called_once_with()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_endscan_fail_check_allowed_with_device_unresponsive(
    tango_context, devices
):

    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", devices)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", cm.get_device().dev_name, elapsed_time
    )
    adapter_factory = HelperAdapterFactory()
    cm.get_device().update_unresponsive(True)
    endscan_command = EndScan(cm, cm.op_state_model, adapter_factory)
    cm.get_device().update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        endscan_command.check_allowed()


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_endscan_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):

    logger.info("%s", tango_context)
    _, endscan_command, _ = get_sdpsln_command_obj(
        EndScan, devices, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(
        InvalidObsStateError,
        match="EndScan command is not allowed",
    ):
        endscan_command.check_allowed()
