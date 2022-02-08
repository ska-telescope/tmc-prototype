import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.release_resources_command import (
    ReleaseResources,
)
from ska_tmc_sdpsubarrayleafnode.exceptions import DeviceUnresponsive

# from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.shraddha
def test_telescope_release_resources_command(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    cm, release_command, my_adapter_factory = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.IDLE
    )
    cm.get_device().obsState == ObsState.EMPTY
    assert release_command.check_allowed()
    (result_code, _) = release_command.do()
    assert result_code == ResultCode.OK
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    # if isinstance(adapter, SdpSubArrayAdapter):
    adapter.proxy.ReleaseResources.assert_called()


@pytest.mark.shraddha
def test_telescope_release_resources_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    # input_parameter = SdpSLNInputParameter(None)
    cm, _ = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    # elapsed_time = time.time() - start_time
    # logger.info(
    #     "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    # )

    adapter_factory = HelperAdapterFactory()

    # include exception in ReleaseResources command
    cm.update_device_obs_state(ObsState.IDLE)
    adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE,
        attrs={"ReleaseAllResources.side_effect": Exception},
    )

    release_command = ReleaseResources(cm, cm.op_state_model, adapter_factory)
    assert release_command.check_allowed()
    (result_code, message) = release_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.shraddha
def test_telescope_release_resources_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, release_command, _ = get_sdpsln_command_obj(
        ReleaseResources, obsstate_value=ObsState.IDLE
    )
    devInfo = cm.get_device()
    devInfo.update_unresponsive(True)
    with pytest.raises(DeviceUnresponsive):
        release_command.check_allowed()
