# TODO : Will get Uncommented after refactoring for command is done.
# import pytest
# from ska_tango_base.commands import ResultCode
# from ska_tmc_common.exceptions import DeviceUnresponsive
# from ska_tmc_common.test_helpers.helper_adapter_factory import (
#     HelperAdapterFactory,
# )

# from ska_tmc_sdpsubarrayleafnode.commands import Off
# from tests.settings import (
#     SDP_SUBARRAY_DEVICE_LOW,
#     SDP_SUBARRAY_DEVICE_MID,
#     create_cm,
#     get_sdpsln_command_obj,
#     logger,
# )


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_off_command(tango_context, devices):
#     logger.info("%s", tango_context)
#     _, off_command, adapter_factory = get_sdpsln_command_obj(
#         Off, devices, None
#     )
#     assert off_command.check_allowed()
#     (result_code, _) = off_command.do()
#     assert result_code == ResultCode.OK
#     adapter = adapter_factory.get_or_create_adapter(devices)
#     adapter.proxy.Off.assert_called_once_with()


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_off_command_fail_sdp_subarray(tango_context, devices):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm("SdpSLNComponentManager", devices)
#     adapter_factory = HelperAdapterFactory()

#     # include exception in TelescopeOff command
#     adapter_factory.get_or_create_adapter(
#         devices, attrs={"Off.side_effect": Exception}
#     )

#     off_command = Off(cm, cm.op_state_model, adapter_factory)
#     assert off_command.check_allowed()
#     (result_code, message) = off_command.do()
#     assert result_code == ResultCode.FAILED
#     assert devices in message


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_off_fail_check_allowed(tango_context, devices):
#     logger.info("%s", tango_context)
#     cm, off_command, _ = get_sdpsln_command_obj(Off, devices, None)
#     devInfo = cm.get_device()
#     devInfo.update_unresponsive(True)
#     with pytest.raises(DeviceUnresponsive):
#         off_command.check_allowed()
