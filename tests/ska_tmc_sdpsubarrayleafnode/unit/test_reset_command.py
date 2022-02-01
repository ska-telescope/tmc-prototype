import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.reset_command import Reset
from ska_tmc_sdpsubarrayleafnode.exceptions import DeviceUnresponsive
from tests.settings import get_sdpsln_command_obj, logger


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
    cm, reset_command, _ = get_sdpsln_command_obj(Reset, None)
    cm.input_parameter.sdp_subarray_dev_name = ""
    with pytest.raises(DeviceUnresponsive):
        reset_command.check_allowed()
