import time

import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.telescope_on_command import (
    TelescopeOn,
)
from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
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


def test_telescope_on_command(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    for adapter in my_adapter_factory.adapters:
        if isinstance(my_adapter_factory.adapters, SdpSubArrayAdapter):
            adapter.proxy.On.assert_called()
            continue


def test_telescope_on_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOn command
    failing_dev = "mid_sdp/elt/subarray_01"

    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeOn.side_effect": Exception}
    )

    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_on_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(CommandNotAllowed):
        on_command.check_allowed()
