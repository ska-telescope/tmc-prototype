import json
import time
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.scan_command import Scan
from ska_tmc_sdpsubarrayleafnode.exceptions import (
    CommandNotAllowed,
    InvalidObsStateError,
)
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm, logger


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
    dev_name = "mid_sdp/elt/subarray_1"

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
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Scan.assert_called()


def test_telescope_scan_command_missing_interface_key(
    tango_context,
):
    logger.info("%s", tango_context)
    scan_command, my_adapter_factory = get_scan_command_obj()

    scan_input_str = get_scan_input_str()
    json_argument = json.loads(scan_input_str)
    json_argument["interface"] = ""
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Scan.assert_called()


def test_telescope_scan_command_fail_subarray(tango_context):
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
    failing_dev = "mid_sdp/elt/subarray_1"
    attrs = {"Scan.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(failing_dev, proxy=subarrayMock)

    scan_command = Scan(cm, cm.op_state_model, my_adapter_factory, skuid)
    cm.update_device_obs_state(failing_dev, ObsState.READY)
    scan_input_str = get_scan_input_str()
    assert scan_command.check_allowed()
    (result_code, message) = scan_command.do(scan_input_str)
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


def test_telescope_scan_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    scan_command, _ = get_scan_command_obj()
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do("")
    assert result_code == ResultCode.FAILED


def test_telescope_scan_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    dev_name = "mid_sdp/elt/subarray_1"

    cm.update_device_obs_state(dev_name, ObsState.IDLE)
    my_adapter_factory = HelperAdapterFactory()
    scan_command = Scan(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(InvalidObsStateError):
        scan_command.check_allowed()


def test_telescope_scan_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    scan_command = Scan(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(CommandNotAllowed):
        scan_command.check_allowed()
