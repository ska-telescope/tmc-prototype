import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import SdpSubArrayAdapter

from ska_tmc_sdpsubarrayleafnode.commands.telescope_on_command import (
    TelescopeOn,
)
from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm_parametrize, logger

SDP_SUBARRAY_DEVICE = "mid_sdp/elt/subarray_1"


@pytest.mark.telescopeon
def test_telescope_on_command(tango_context):
    logger.info("%s", tango_context)
    # cm, start_time = create_cm()
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(my_adapter_factory.adapters, SdpSubArrayAdapter):
        adapter.proxy.On.assert_called()


@pytest.mark.telescopeon
def test_telescope_on_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    # cm, start_time = create_cm()
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOn command
    failing_dev = "mid_sdp/elt/subarray_1"

    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeOn.side_effect": Exception}
    )

    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.telescopeon
def test_telescope_on_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm_parametrize(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    # cm, start_time = create_cm()
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()
    cm.input_parameter.sdp_subarray_dev_name = ""
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(CommandNotAllowed):
        on_command.check_allowed()
