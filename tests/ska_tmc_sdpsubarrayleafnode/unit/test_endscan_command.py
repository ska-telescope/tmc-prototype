import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.endscan_command import EndScan
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    CommandNotAllowed,
    InvalidObsStateError,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import SDP_SUBARRAY_DEVICE, create_cm, logger


def test_endscan_command(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    dev_name = "mid_sdp/elt/subarray_1"
    cm.update_device_obs_state(dev_name, ObsState.SCANNING)
    endscan_command = EndScan(cm, cm.op_state_model, my_adapter_factory)

    cm.get_device(dev_name).obsState == ObsState.READY

    assert endscan_command.check_allowed()
    (result_code, _) = endscan_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.EndScan.assert_called()


def test_endscan_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    endscan_command = EndScan(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(CommandNotAllowed):
        endscan_command.check_allowed()


def test_endscan_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_1"

    cm.update_device_obs_state(dev_name, ObsState.IDLE)
    my_adapter_factory = HelperAdapterFactory()
    release_command = EndScan(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(InvalidObsStateError):
        release_command.check_allowed()
