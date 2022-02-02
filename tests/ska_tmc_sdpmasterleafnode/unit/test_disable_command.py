import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import MasterAdapter

from ska_tmc_sdpmasterleafnode.commands.disable_command import Disable
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
def test_disable_command(tango_context):
    logger.info("%s", tango_context)
    _, disable_command, adapter_factory = get_sdpmln_command_obj(Disable)
    assert disable_command.check_allowed()
    (result_code, _) = disable_command.do()
    assert result_code == ResultCode.OK
    # dev_name = SDP_MASTER_DEVICE
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    if isinstance(adapter_factory.adapters, MasterAdapter):
        adapter.proxy.Disable.assert_called()


@pytest.mark.sdpmln
def test_disable_command_fail_sdp_master(tango_context):
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

    # include exception in Disable command
    failing_dev = "mid_sdp/elt/master"

    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"Disable.side_effect": Exception}
    )

    disable_command = Disable(cm, cm.op_state_model, my_adapter_factory)
    assert disable_command.check_allowed()
    (result_code, message) = disable_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpmln
def test_disable_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, disable_command, _ = get_sdpmln_command_obj(Disable)
    cm.input_parameter.sdp_master_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        disable_command.check_allowed()
