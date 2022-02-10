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
    DeviceUnresponsive,
    InvalidObsStateError,
)

# from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


def get_scan_input_str(scan_input_file="command_Scan.json"):
    path = join(dirname(__file__), "..", "..", "data", scan_input_file)
    with open(path, "r") as f:
        scan_input_file = f.read()
    return scan_input_file


@pytest.mark.sdpsln
def test_telescope_scan_command(tango_context):
    logger.info("%s", tango_context)
    cm, scan_command, my_adapter_factory = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.READY
    )

    scan_input_str = get_scan_input_str()
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do(scan_input_str)
    assert result_code == ResultCode.OK
    # dev_name = "mid_sdp/elt/subarray_1"
    cm.get_device().obsState == ObsState.EMPTY
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Scan.assert_called()


@pytest.mark.sdpsln
def test_telescope_scan_command_missing_interface_key(
    tango_context,
):
    logger.info("%s", tango_context)
    _, scan_command, my_adapter_factory = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.READY
    )
    scan_input_str = get_scan_input_str()
    json_argument = json.loads(scan_input_str)
    json_argument["interface"] = ""
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do(json.dumps(json_argument))
    assert result_code == ResultCode.OK
    # dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(SDP_SUBARRAY_DEVICE)
    if isinstance(adapter, SdpSubArrayAdapter):
        adapter.proxy.Scan.assert_called()


@pytest.mark.sdpsln
def test_telescope_scan_command_fail_subarray(tango_context):
    logger.info("%s", tango_context)
    # input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm("SdpSLNComponentManager", SDP_SUBARRAY_DEVICE)
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s device in %s", len(SDP_SUBARRAY_DEVICE), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()

    attrs = {"fetch_skuid.return_value": 123}
    skuid = mock.Mock(**attrs)

    # include exception in AssignResources command
    # failing_dev = "mid_sdp/elt/subarray_1"
    attrs = {"Scan.side_effect": Exception}
    subarrayMock = mock.Mock(**attrs)
    my_adapter_factory.get_or_create_adapter(
        SDP_SUBARRAY_DEVICE, proxy=subarrayMock
    )

    scan_command = Scan(cm, cm.op_state_model, my_adapter_factory, skuid)
    cm.update_device_obs_state(ObsState.READY)
    scan_input_str = get_scan_input_str()
    assert scan_command.check_allowed()
    (result_code, message) = scan_command.do(scan_input_str)
    assert result_code == ResultCode.FAILED
    assert SDP_SUBARRAY_DEVICE in message


@pytest.mark.sdpsln
def test_telescope_scan_command_empty_input_json(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    _, scan_command, _ = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.READY
    )
    assert scan_command.check_allowed()
    (result_code, _) = scan_command.do("")
    assert result_code == ResultCode.FAILED


@pytest.mark.sdpsln
def test_telescope_scan_command_fail_check_allowed_with_invalid_obsState(
    tango_context,
):

    logger.info("%s", tango_context)
    _, scan_command, _ = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.IDLE
    )
    with pytest.raises(InvalidObsStateError):
        scan_command.check_allowed()


@pytest.mark.sdpsln
@pytest.mark.abort
def test_telescope_scan_fail_check_allowed_with_device_undesponsive(
    tango_context,
):

    logger.info("%s", tango_context)
    cm, scan_command, my_adapter_factory = get_sdpsln_command_obj(
        Scan, obsstate_value=ObsState.SCANNING
    )
    device_info = cm.get_device()
    device_info.update_unresponsive(True)
    # scan_command = Scan(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(DeviceUnresponsive):
        scan_command.check_allowed()
