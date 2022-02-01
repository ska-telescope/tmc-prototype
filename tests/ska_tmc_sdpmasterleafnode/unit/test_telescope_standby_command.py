import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import BaseAdapter

from ska_tmc_sdpmasterleafnode.commands.telescope_standby_command import TelescopeStandby

from ska_tmc_sdpmasterleafnode.exceptions import DeviceUnresponsive
from ska_tmc_sdpmasterleafnode.model.input import SdpMLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (  
    create_cm,
    SDP_MASTER_DEVICE,
    get_sdpmln_command_obj,
    logger,
)


@pytest.mark.sdpmln
def test_telescope_standby_command(tango_context):
    logger.info("%s", tango_context)
    _, standby_command, adapter_factory = get_sdpmln_command_obj(TelescopeStandby, None)
    assert standby_command.check_allowed()
    (result_code, _) = standby_command.do()
    assert result_code == ResultCode.OK
    # dev_name = SDP_MASTER_DEVICE
    adapter = adapter_factory.get_or_create_adapter(SDP_MASTER_DEVICE)
    if isinstance(adapter_factory.adapters, BaseAdapter):
        adapter.proxy.standby.assert_called()


@pytest.mark.sdpmln
def test_telescope_standby_command_fail_sdp_master(tango_context):
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

    # include exception in TelescopeStandby command
    failing_dev = "mid_sdp/elt/master"

    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeStandby.side_effect": Exception}
    )

    standby_command = TelescopeStandby(cm, cm.op_state_model, my_adapter_factory)
    assert standby_command.check_allowed()
    (result_code, message) = standby_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpmln
def test_telescope_on_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, standby_command, _ = get_sdpmln_command_obj(TelescopeStandby, None)
    cm.input_parameter.sdp_master_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        standby_command.check_allowed()
