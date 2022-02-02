import time

import pytest
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import MasterAdapter

from ska_tmc_sdpmasterleafnode.commands.telescope_off_command import (
    TelescopeOff,
)
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
def test_telescope_off_command(tango_context):
    logger.info("%s", tango_context)
    _, off_command, my_adapter_factory = get_sdpmln_command_obj(TelescopeOff)
    assert off_command.check_allowed()
    (result_code, _) = off_command.do()
    assert result_code == ResultCode.OK
    dev_name = SDP_MASTER_DEVICE
    adapter = my_adapter_factory.get_or_create_adapter(dev_name)
    if isinstance(adapter, MasterAdapter):
        adapter.proxy.Off.assert_called()


@pytest.mark.sdpmln
def test_telescope_off_command_fail_sdp_master(tango_context):
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

    # include exception in TelescopeOff command
    failing_dev = SDP_MASTER_DEVICE
    my_adapter_factory.get_or_create_adapter(
        failing_dev, attrs={"TelescopeOff.side_effect": Exception}
    )

    off_command = TelescopeOff(cm, cm.op_state_model, my_adapter_factory)
    assert off_command.check_allowed()
    (result_code, message) = off_command.do()
    assert result_code == ResultCode.FAILED
    assert failing_dev in message


@pytest.mark.sdpmln
def test_telescope_off_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    cm, off_command, my_adapter_factory = get_sdpmln_command_obj(TelescopeOff)
    cm.input_parameter.sdp_master_dev_name = ""
    off_command = TelescopeOff(cm, cm.op_state_model, my_adapter_factory)
    with pytest.raises(DeviceUnresponsive):
        off_command.check_allowed()
