import time

import mock
import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.reset_command import Reset
from ska_tmc_sdpsubarrayleafnode.exceptions import CommandNotAllowed
from ska_tmc_sdpsubarrayleafnode.model.input import SdpSLNInputParameter
from tests.helpers.helper_adapter_factory import HelperAdapterFactory
from tests.settings import (
    SDP_SUBARRAY_DEVICE,
    create_cm,
    get_sdpsln_command_obj,
    logger,
)

# def get_reset_command_obj():
#     input_parameter = SdpSLNInputParameter(None)
#     cm, start_time = create_cm(
#         "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
#     )
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s devices in %s", len(cm.checked_devices), elapsed_time
#     )

#     my_adapter_factory = HelperAdapterFactory()

#     attrs = {"fetch_skuid.return_value": 123}
#     skuid = mock.Mock(**attrs)

#     reset_command = Reset(cm, cm.op_state_model, my_adapter_factory, skuid)
#     return reset_command, my_adapter_factory


@pytest.mark.sdpsaln
def test_telescope_reset_command(tango_context):
    logger.info("%s", tango_context)
    _, reset_command, _ = get_sdpsln_command_obj(Reset, None)
    assert reset_command.check_allowed()
    (result_code, _) = reset_command.do()
    assert result_code == ResultCode.OK


@pytest.mark.sdpsaln
def test_telescope_reset_fail_check_allowed(tango_context):

    logger.info("%s", tango_context)
    # input_parameter = SdpSLNInputParameter(None)
    # cm, start_time = create_cm(
    #     "SdpSLNComponentManager", input_parameter, SDP_SUBARRAY_DEVICE
    # )
    # elapsed_time = time.time() - start_time
    # logger.info(
    #     "checked %s devices in %s", len(cm.checked_devices), elapsed_time
    # )

    # my_adapter_factory = HelperAdapterFactory()
    cm, reset_command, _ = get_sdpsln_command_obj(Reset, None)
    cm.input_parameter.sdp_subarray_dev_name = ""
    with pytest.raises(CommandNotAllowed):
        reset_command.check_allowed()
