import json
import time
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.release_resources_command import (
    ReleaseAllResources,
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


def get_release_resources_command_obj():
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    release_command = ReleaseAllResources(
        cm, cm.op_state_model, my_adapter_factory
    )
    return release_command, my_adapter_factory


def test_telescope_release_resources_command(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    release_command, my_adapter_factory = get_release_resources_command_obj()

    assert release_command.check_allowed()
    (result_code, _) = release_command.do()
    assert result_code == ResultCode.OK
    for adapter in my_adapter_factory.adapters:
        if isinstance(adapter, SdpSubArrayAdapter):
            adapter.proxy.ReleaseResources.assert_called()


def test_telescope_release_resources_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    # include exception in ReleaseResources command
    failing_dev = "mid_sdp/elt/subarray_01"
    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"ReleaseAllResources.side_effect": Exception}
    )

    release_command = ReleaseAllResources(
        cm, cm.op_state_model, my_adapter_factory
    )
    assert release_command.check_allowed()
    (result_code, message) = release_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_release_resources_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    release_command = ReleaseAllResources(
        cm, cm.op_state_model, my_adapter_factory
    )
    with pytest.raises(CommandNotAllowed):
        release_command.check_allowed()
