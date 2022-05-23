import json
import time
from os.path import dirname, join

import mock
import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands import Scan
from tests.settings import create_cm, get_sdpsln_command_obj, logger


def get_scan_input_str(scan_input_file="command_Scan.json"):
    path = join(dirname(__file__), "..", "..", "data", scan_input_file)
    with open(path, "r") as f:
        scan_input_file = f.read()
    return scan_input_file


@pytest.mark.sdpsln
def test_scan_command(tango_context, sdp_subarray_device):
    logger.info("%s", tango_context)
    cm, scan_command, adapter_factory = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.READY
    )

    scan_input_str = get_scan_input_str()
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do(scan_input_str)
    assert result_code == ResultCode.OK
    cm.get_device().obs_state == ObsState.EMPTY
    adapter = adapter_factory.get_or_create_adapter(sdp_subarray_device)
    adapter.proxy.Scan.assert_called()


@pytest.mark.sdpsln
def test_scan_command_missing_interface_key(
    tango_context, sdp_subarray_device
):
    logger.info("%s", tango_context)
    _, scan_command, adapter_factory = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.READY
    )
    scan_input_str = get_scan_input_str()
    json_argument = json.loads(scan_input_str)
    json_argument["interface"] = ""
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(sdp_subarray_device)
    adapter.proxy.Scan.assert_called()


@pytest.mark.sdpsln
def test_scan_command_fail_subarray(tango_context, sdp_subarray_device):
    logger.info("%s", tango_context)
    cm, start_time = create_cm("SdpSLNComponentManager", sdp_subarray_device)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", len(sdp_subarray_device), elapsed_time
    )

    adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    attrs = {"Scan.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    adapter_factory.get_or_create_adapter(
        sdp_subarray_device, proxy=subarrayMock
    )

    scan_command = Scan(cm, cm.op_state_model, adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.READY)
    scan_input_str = get_scan_input_str()
    assert scan_command.check_allowed()
    (result_code, message) = scan_command.do(scan_input_str)
    assert result_code == ResultCode.FAILED
    assert sdp_subarray_device in message


@pytest.mark.sdpsln
def test_scan_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    _, scan_command, _ = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.READY
    )
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do("")
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsln
def test_scan_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, scan_command, _ = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(
        InvalidObsStateError,
        match=f"""The current observation state for observation is
            {ObsState.IDLE}""",
    ):
        scan_command.check_allowed()


@pytest.mark.sdpsln
def test_scan_fail_check_allowed_with_device_undesponsive(
    tango_context,
):
    logger.info("%s", tango_context)
    cm, scan_command, _ = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.SCANNING
    )
    device_info = cm.get_device()
    device_info.update_unresponsive(True)
    with pytest.raises(
        DeviceUnresponsive, match="SDP subarray device is not available"
    ):
        scan_command.check_allowed()
