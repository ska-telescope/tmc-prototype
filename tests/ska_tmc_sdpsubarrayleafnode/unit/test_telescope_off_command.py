import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)

from ska_tmc_sdpsubarrayleafnode.commands.telescope_off_command import (
    TelescopeOff,
)
from ska_tmc_sdpsubarrayleafnode.exceptions import DeviceUnresponsive
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)


@pytest.mark.sdpsln
def test_telescope_off_command(tango_context):
    logger.info("%s", tango_context)
    _, off_command, my_adapter_factory = get_sdpsln_command_obj(
        TelescopeOff, None
    )
    assert off_command.check_allowed()
    (result_code, _) = off_command.do()
    assert result_code == ResultCode.OK
    dev_name = "mid_sdp/elt/subarray_1"
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    adapter.proxy.Off.assert_called()


@pytest.mark.sdpsln
def test_telescope_off_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpSLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOff command
    failing_dev = "mid_sdp/elt/subarray_1"
    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeOff.side_effect": Exception}
    )

    off_command = TelescopeOff(cm, cm.op_state_model, my_adapter_factory)
    assert off_command.check_allowed()
    (result_code, message) = off_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpsln
def test_telescope_off_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, off_command, my_adapter_factory = get_sdpsln_command_obj(
        TelescopeOff, None
    )
    cm.input_parameter.sdp_subarray_dev_name = ""
    off_command = TelescopeOff(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(DeviceUnresponsive):
        off_command.check_allowed()
