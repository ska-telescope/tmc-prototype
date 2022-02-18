import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.release_resources_command import (
    ReleaseResources,
)
from ska_tmc_sdpsubarrayleafnode.exceptions import DeviceUnresponsive
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_release_resources_command(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    cm, release_command, my_adapter_factory = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.IDLE
    )
    dev_name = "mid_sdp/elt/subarray_1"
    cm.get_device(dev_name).obsState == ObsState.EMPTY
    assert release_command.check_allowed()
    (result_code, _) = release_command.do()
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    adapter.proxy.ReleaseResources.assert_called()


@pytest.mark.sdpsln
def test_telescope_release_resources_command_fail_subarray(tango_context):
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

    # include exception in ReleaseResources command
    failing_dev = "mid_sdp/elt/subarray_1"
    cm.update_device_obs_state(failing_dev, ObsState.IDLE)
    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"ReleaseAllResources.side_effect": Exception}
    )

    release_command = ReleaseResources(
        cm, cm.op_state_model, my_adapter_factory
    )
    assert release_command.check_allowed()
    (result_code, message) = release_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpsln
def test_telescope_release_resources_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.IDLE
    )
    cm.input_parameter.sdp_subarray_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        release_command.check_allowed()
