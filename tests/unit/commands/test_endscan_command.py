import time

import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.endscan_command import EndScan
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    CommandNotAllowed,
    InvalidObsStateError,
)
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm, logger


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": SKABaseDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_01"},
            ],
        },
    )


def test_endscan_command(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    dev_name = "mid_sdp/elt/subarray_01"
    cm.update_device_obs_state(dev_name, ObsState.SCANNING)
    endscan_command = EndScan(cm, cm.op_state_model, my_adapter_factory)
    assert endscan_command.check_allowed()
    (result_code, _) = endscan_command.do()
    assert result_code == ResultCode.OK
    for adapter in my_adapter_factory.adapters:
        if isinstance(adapter, SdpSubArrayAdapter):
            adapter.proxy.EndScan.assert_called()


# def test_endscan_command_fail_sdp_subarray(tango_context):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm()
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s devices in %s", len(cm.checked_devices), elapsed_time
#     )
#     my_adapter_factory = HelperAdapterFactory()

#     # include exception in EndScan command
#     failing_dev = "mid_sdp/elt/subarray_01"
#     cm.update_device_obs_state(failing_dev, ObsState.SCANNING)
#     my_adapter_factory.get_or_create_adapter(
#         failing_dev, attrs={"EndScan.side_effect": Exception}
#     )

#     endscan_command = EndScan(cm, cm.op_state_model, my_adapter_factory)
#     assert endscan_command.check_allowed()
#     (result_code, message) = endscan_command.do()
#     assert result_code == ResultCode.FAILED
#     assert failing_dev in message


def test_endscan_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, start_time = create_cm()
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
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_01"

    cm.update_device_obs_state(dev_name, ObsState.IDLE)
    my_adapter_factory = HelperAdapterFactory()
    release_command = EndScan(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(InvalidObsStateError):
        release_command.check_allowed()
