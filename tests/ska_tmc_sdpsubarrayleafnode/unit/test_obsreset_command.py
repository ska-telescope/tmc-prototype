import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.obsreset_command import ObsReset
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    CommandNotAllowed,
    InvalidObsStateError,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm_parametrize, logger

SDP_SUBARRAY_DEVICE = "mid_sdp/elt/subarray_1"


def get_obsreset_command_obj():
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_1"

    cm.update_device_obs_state(dev_name, ObsState.ABORTED)
    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)  # is skauid required here?

    obsreset_command = ObsReset(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    cm.get_device(dev_name).obsState == ObsState.IDLE
    return obsreset_command, my_adapter_factory


def test_telescope_obsreset_command(tango_context):
    logger.info("%s", tango_context)
    obsreset_command, my_adapter_factory = get_obsreset_command_obj()

    assert obsreset_command.check_allowed()
    (result_code, _) = obsreset_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.ObsReset.assert_called()


def test_telescope_obsreset_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in ObsReset command
    failing_dev = "mid_sdp/elt/subarray_1"
    attrs = {"ObsReset.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    obsreset_command = ObsReset(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    cm.update_device_obs_state(failing_dev, ObsState.ABORTED)
    assert obsreset_command.check_allowed()
    (result_code, message) = obsreset_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_obsreset_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_1"

    cm.update_device_obs_state(dev_name, ObsState.IDLE)
    my_adapter_factory = HelperAdapterFactory()
    obsreset_command = ObsReset(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(InvalidObsStateError):
        obsreset_command.check_allowed()


def test_telescope_obsreset_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    obsreset_command = ObsReset(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(CommandNotAllowed):
        obsreset_command.check_allowed()
