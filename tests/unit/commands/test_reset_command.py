import time

import mock
import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.reset_command import Reset
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


def get_reset_command_obj():
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)  # is skauid required here?

    reset_command = Reset(cm, cm.op_state_model, my_adapter_factory, skuid)
    return reset_command, my_adapter_factory


def test_telescope_reset_command(tango_context):
    logger.info("%s", tango_context)
    reset_command, _ = get_reset_command_obj()

    assert reset_command.check_allowed()
    (result_code, _) = reset_command.do()
    assert result_code == ResultCode.OK
    # for adapter in my_adapter_factory.adapters:
    #     adapter.proxy.Reset.assert_called()


def test_telescope_reset_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    reset_command = Reset(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(CommandNotAllowed):
        reset_command.check_allowed()
