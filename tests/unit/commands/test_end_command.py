import time

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.end_command import End
from ska_tmc_sdpsubarrayleafnode.exceptions import InvalidObsStateError
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm, logger


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

    end_command = End(cm, cm.op_state_model, my_adapter_factory, skuid)
    cm.get_device(dev_name).obsState == ObsState.IDLE

    return end_command, my_adapter_factory


def test_telescope_end_command(tango_context):
    logger.info("%s", tango_context)
    end_command, my_adapter_factory = get_end_command_obj()

    assert end_command.check_allowed()
    (result_code, _) = end_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_01"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
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
    attrs = {"End.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    end_command = End(cm, cm.op_state_model, my_adapter_factory, skuid)
    cm.update_device_obs_state(failing_dev, ObsState.READY)
    assert end_command.check_allowed()
    (result_code, message) = end_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_end_command_fail_check_allowed_with_invalid_obsState(
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
    end_command = End(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(InvalidObsStateError):
        end_command.check_allowed()
