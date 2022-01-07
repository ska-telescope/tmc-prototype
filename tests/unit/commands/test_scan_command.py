import time
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
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


def get_scan_input_str(scan_input_file="command_Scan.json"):
    path = join(dirname(__file__), "..", "..", "data", scan_input_file)
    with open(path, "r") as f:
        scan_input_file = f.read()
    return scan_input_file


def get_scan_command_obj():
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_01"

    cm.update_device_obs_state(dev_name, ObsState.READY)
    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)  # is skauid required here?

    scan_command = Scan(cm, cm.op_state_model, my_adapter_factory, skuid)
    return scan_command, my_adapter_factory


def test_telescope_scan_command(tango_context):
    logger.info("%s", tango_context)
    scan_command, my_adapter_factory = get_scan_command_obj()

    scan_input_str = get_scan_input_str()
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do(scan_input_str)
    assert result_code == ResultCode.OK
    for adapter in my_adapter_factory.adapters:
        if isinstance(adapter, SdpSubArrayAdapter):
            adapter.proxy.Scan.assert_called()


# def test_telescope_configure_resources_command_missing_interface_key(
#     tango_context,
# ):
#     logger.info("%s", tango_context)
#     configure_command, my_adapter_factory = get_configure_command_obj()

#     configure_input_str = get_configure_input_str()
#     json_argument = json.loads(configure_input_str)
#     json_argument["interface"] = ""
#     assert configure_command.check_allowed()
#     (result_code, _) = configure_command.do(json.dumps(json_argument))
#     assert result_code == ResultCode.OK
#     for adapter in my_adapter_factory.adapters:
#         if isinstance(adapter, SdpSubArrayAdapter):
#             adapter.proxy.Configure.assert_called()
