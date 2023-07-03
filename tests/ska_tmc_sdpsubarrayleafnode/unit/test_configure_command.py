from os.path import dirname, join

import pytest
from ska_tango_base.commands import ResultCode, TaskStatus
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import Configure
from tests.settings import (
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
    create_cm,
    logger,
)


def get_configure_input_str(configure_input_file="command_Configure.json"):
    path = join(dirname(__file__), "..", "..", "data", configure_input_file)
    with open(path, "r") as f:
        configure_input_str = f.read()
    return configure_input_str


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_configure_command(tango_context, devices, task_callback):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    configure_input_str = get_configure_input_str()
    cm.configure(configure_input_str, task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.COMPLETED, "result": ResultCode.OK}
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_configure_command_fail_subarray(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    adapter_factory = HelperAdapterFactory()
    failing_dev = devices
    configure_input_str = get_configure_input_str()

    adapter_factory.get_or_create_adapter(
        failing_dev,
        AdapterType.SUBARRAY,
        attrs={"Configure.side_effect": Exception},
    )
    configure_command = Configure(cm, logger)
    configure_command.adapter_factory = adapter_factory
    configure_command.configure(configure_input_str, logger, task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.FAILED
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_configure_command_empty_input_json(
    tango_context, devices, task_callback
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    configure_input_str = ""
    cm.configure(configure_input_str, task_callback=task_callback)
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.QUEUED}
    )
    task_callback.assert_against_call(
        call_kwargs={"status": TaskStatus.IN_PROGRESS}
    )
    task_callback.assert_against_call(
        status=TaskStatus.COMPLETED, result=ResultCode.FAILED
    )


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_configure_command_fail_check_allowed_with_invalid_obsState(
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm.update_device_obs_state(ObsState.EMPTY)
    with pytest.raises(InvalidObsStateError):
        cm.is_command_allowed("Configure")


@pytest.mark.sdpsln
@pytest.mark.parametrize(
    "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
)
def test_telescope_configure_command_fail_check_allowed_with_device_unresponsive(  # noqa:E501
    tango_context, devices
):
    logger.info("%s", tango_context)
    cm = create_cm("SdpSLNComponentManager", devices)
    cm._device = DeviceInfo(devices, _unresponsive=True)
    with pytest.raises(DeviceUnresponsive):
        cm.is_command_allowed("configure")
