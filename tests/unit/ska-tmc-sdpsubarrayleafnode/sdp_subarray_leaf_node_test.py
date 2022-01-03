import time

import pytest
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.telescope_on_command import (
    TelescopeOn,
)
from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
from ska_tmc_sdpsubarrayleafnode.manager.adapters import SdpsubarrayAdapter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import create_cm, logger


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": SKABaseDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_01"},
            ],
        },
    )


def test_telescope_on_command(tango_context):
    logger.info("%s", tango_context)
    # import debugpy; debugpy.debug_this_thread()
    cm, start_time = create_cm()
    # num_faulty = count_faulty_devices(cm)
    # assert num_faulty == 0
    elapsed_time = time.time() - start_time
    logger.info(
        "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    )

    my_adapter_factory = HelperAdapterFactory()
    on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
    assert on_command.check_allowed()
    (result_code, _) = on_command.do()
    assert result_code == ResultCode.OK
    for adapter in my_adapter_factory.adapters:
        # if isinstance(adapter, SdpsubarrayAdapter):
        #     adapter.proxy.SetStandbyFPMode.assert_called()
        #     adapter.proxy.SetOperateMode.assert_called()
        #     continue
        # if isinstance(adapter, SubArrayAdapter):
        #     adapter.proxy.TelescopeOn.assert_called()
        #     continue

        adapter.proxy.TelescopeOn.assert_called()


# def test_telescope_on_command_fail_subarray(tango_context):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm()
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s devices in %s", len(cm.checked_devices), elapsed_time
#     )
#     my_adapter_factory = HelperAdapterFactory()

#     # include exception in TelescopeOn command
#     failing_dev = "ska_mid/tm_subarray_node/1"

#     my_adapter_factory.get_or_create_adapter(
#         failing_dev, attrs={"TelescopeOn.side_effect": Exception}
#     )

#     on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
#     assert on_command.check_allowed()
#     (result_code, message) = on_command.do()
#     assert result_code == ResultCode.FAILED
#     assert failing_dev in message


# def test_telescope_on_command_fail_sdp(tango_context):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm()
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s devices in %s", len(cm.checked_devices), elapsed_time
#     )
#     my_adapter_factory = HelperAdapterFactory()

#     # include exception in TelescopeOn command
#     failing_dev = "mid_sdp/elt/master"
#     my_adapter_factory.get_or_create_adapter(
#         failing_dev, attrs={"TelescopeOn.side_effect": Exception}
#     )

#     on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
#     assert on_command.check_allowed()
#     (result_code, message) = on_command.do()
#     assert result_code == ResultCode.FAILED
#     assert failing_dev in message


# def test_telescope_on_fail_check_allowed(tango_context):

#     logger.info("%s", tango_context)
#     cm, start_time = create_cm()
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s devices in %s", len(cm.checked_devices), elapsed_time
#     )
#     my_adapter_factory = HelperAdapterFactory()
#     cm.input_parameter.tm_dish_dev_names = []
#     on_command = TelescopeOn(cm, cm.op_state_model, my_adapter_factory)
#     with pytest.raises(CommandNotAllowed):
#         on_command.check_allowed()
