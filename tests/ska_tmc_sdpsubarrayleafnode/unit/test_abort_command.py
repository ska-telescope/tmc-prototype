import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.abort_command import Abort
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    DeviceUnresponsive,
    InvalidObsStateError,
)
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


def test_telescope_abort_command(tango_context):
    logger.info("%s", tango_context)
    _, abort_command, my_adapter_factory = get_sdpsln_command_obj(
        Abort, ObsState.CONFIGURING
    )

    assert abort_command.check_allowed()
    (result_code, _) = abort_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Abort.assert_called()


def test_telescope_abort_command_fail_subarray(tango_context):
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
    attrs = {"Abort.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    abort_command = Abort(cm, cm.op_state_model, my_adapter_factory, skuid)
    cm.update_device_obs_state(failing_dev, ObsState.CONFIGURING)
    assert abort_command.check_allowed()
    (result_code, message) = abort_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message
    cm.get_device(failing_dev).obsState == ObsState.ABORTED


def test_telescope_abort_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, abort_command, _ = get_sdpsln_command_obj(Abort, ObsState.ABORTED)
    with pytest.raises(InvalidObsStateError):
        abort_command.check_allowed()


def test_telescope_abort_command_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, abort_command, _ = get_sdpsln_command_obj(Abort, ObsState.ABORTED)
    cm.input_parameter.sdp_subarray_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        abort_command.check_allowed()