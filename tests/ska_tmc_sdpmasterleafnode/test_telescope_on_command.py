import time

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpmasterleafnode.commands.telescope_on_command import TelescopeOn
from ska_tmc_sdpmasterleafnode.exceptions import DeviceUnresponsive
from ska_tmc_sdpmasterleafnode.manager.adapters import SdpMasterAdapter
from ska_tmc_sdpmasterleafnode.model.input import SdpMLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_MASTER_DEVICE,
    create_cm,
    get_sdpmln_command_obj,
    logger,
)

# TODO: Uncomment below imports while using Adapter class from ska-tmc-common library
# from ska_tmc_common.adapters import SdpMasterAdapter


@pytest.mark.sdpmln
def test_telescope_on_command(tango_context):
    logger.info("%s", tango_context)
    _, on_command, adapter_factory = get_sdpmln_command_obj(TelescopeOn)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    # dev_name = SDP_MASTER_DEVICE
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    if isinstance(adapter_factory.adapters, SdpMasterAdapter):
        adapter.proxy.On.assert_called()


@pytest.mark.sdpmln
def test_telescope_on_command_fail_sdp_subarray(tango_context):
    logger.info("%s", tango_context)
    input_parameter = SdpMLNInputParameter(None)
    cm, start_time = create_cm(
        "SdpMLNComponentManager", input_parameter, SDP_MASTER_DEVICE
    )
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )
    my_adapter_factory = HelperAdapterFactory()

    # include exception in TelescopeOn command
    failing_dev = SDP_MASTER_DEVICE
    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeOn.side_effect": Exception}
    )

    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assert on_command.check_allowed()
    (result_code, message) = on_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpmln
def test_telescope_on_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, on_command, _ = get_sdpmln_command_obj(TelescopeOn)
    cm.input_parameter.sdp_master_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        on_command.check_allowed()
