import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import MasterAdapter

from ska_tmc_sdpmasterleafnode.commands.telescope_on_command import TelescopeOn
from ska_tmc_sdpmasterleafnode.exceptions import DeviceUnresponsive
from ska_tmc_sdpmasterleafnode.model.input import SdpMLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_MASTER_DEVICE,
    create_cm,
    get_sdpmln_command_obj,
    logger,
)


@pytest.mark.sdpmln
def test_telescope_on_command(tango_context):
    logger.info("%s", tango_context)
    _, on_command, adapter_factory = get_sdpmln_command_obj(TelescopeOn)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    adapter.proxy.On.assert_called()


@pytest.mark.sdpmln
def test_telescope_on_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpMLNInputParameter(None)
    cm, _ = create_cm(
        "SdpMLNComponentManager", input_parameter, SDP_MASTER_DEVICE
    )
    # elapsed_time = time.time() - start_time
    # logger.info(
    #     "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    # )
    adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOn command
    adapter_factory.get_or_create_adapter(
        SDP_MASTER_DEVICE, attrs={"TelescopeOn.side_effect": Exception}
    )

    on_command = TelescopeOn(cm, cm.op_state_model, adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert SDP_MASTER_DEVICE in message


@pytest.mark.sdpmln
def test_telescope_on_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, on_command, _ = get_sdpmln_command_obj(TelescopeOn)
    cm.input_parameter.sdp_master_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        on_command.check_allowed()
