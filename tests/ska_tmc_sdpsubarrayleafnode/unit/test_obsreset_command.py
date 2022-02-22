import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.obsreset_command import ObsReset
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_obsreset_command(tango_context):
    logger.info("%s", tango_context)
    # obsreset_command, my_adapter_factory = get_obsreset_command_obj()
    cm, obsreset_command, my_adapter_factory = get_sdpsln_command_obj(
        ObsReset, obsstate_value=ObsState.ABORTED
    )
    assert obsreset_command.check_allowed()
    (result_code, _) = obsreset_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    cm.get_device(dev_name).obsState == ObsState.IDLE
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    adapter.proxy.ObsReset.assert_called()


@pytest.mark.sdpsln
def test_telescope_obsreset_command_fail_subarray(tango_context):
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
def test_telescope_obsreset_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, obsreset_command, my_adapter_factory = get_sdpsln_command_obj(
        ObsReset, obsstate_value=ObsState.IDLE
    )
    cm.input_parameter.sdp_subarray_dev_name = ""
    obsreset_command = ObsReset(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(DeviceUnresponsive):
        obsreset_command.check_allowed()
