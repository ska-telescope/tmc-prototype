import json
import time
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.end_command import End
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


def get_end_command_obj():
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_01"

    cm.update_device_obs_state(dev_name, ObsState.READY)
    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    end_command = End(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    return end_command, my_adapter_factory


def test_telescope_end_command(tango_context):
    logger.info("%s", tango_context)
    end_command, my_adapter_factory = get_end_command_obj()

    end_input_str = get_end_input_str()
    assert end_command.check_allowed()
    (result_code, _) = end_command.do(end_input_str)
    assert result_code == ResultCode.OK
    for adapter in my_adapter_factory.adapters:
        if isinstance(adapter, SdpSubArrayAdapter):
            adapter.proxy.End.assert_called()


def test_telescope_assign_resources_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    failing_dev = "mid_sdp/elt/subarray_01"
    attrs = {"AssignResources.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    end_command = End(
        cm, cm.op_state_model, my_adapter_factory, skuid
    )
    cm.update_device_obs_state(failing_dev, ObsState.READY)
    end_input_str = get_end_input_str()
    assert end_command.check_allowed()
    (result_code, message) = end_command.do(end_input_str)
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_end_command_fail_check_allowed_with_invalid_obsState(tango_context,):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
    "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_01"

    cm.update_device_obs_state(dev_name, ObsState.IDLE)
    my_adapter_factory = HelperAdapterFactory()
    # cm.input_parameter.sdp_subarray_dev_name = ""
    end_command = End(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(InvalidObsStateError):
        end_command.check_allowed()
