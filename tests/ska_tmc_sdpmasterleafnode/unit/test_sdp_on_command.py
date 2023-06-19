# TODO : Will get Uncommented after refactoring for command is done.
# import pytest
# from ska_tango_base.commands import ResultCode
# from ska_tmc_common.device_info import DeviceInfo
# from ska_tmc_common.exceptions import DeviceUnresponsive
# from ska_tmc_common.test_helpers.helper_adapter_factory import (
#     HelperAdapterFactory,
# )

# from ska_tmc_sdpmasterleafnode.commands import On
# from tests.settings import (
#     SDP_MASTER_DEVICE_LOW,
#     SDP_MASTER_DEVICE_MID,
#     create_cm,
#     get_sdpmln_command_obj,
# )


# @pytest.mark.parametrize(
#     "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
# )
# def test_on_command(tango_context, sdp_master_device):
#     _, on_command, adapter_factory = get_sdpmln_command_obj(
#         On, sdp_master_device
#     )
#     assert on_command.check_allowed()
#     (result_code, _) = on_command.do()
#     assert result_code == ResultCode.OK
#     adapter = adapter_factory.get_or_create_adapter(sdp_master_device)
#     adapter.proxy.On.assert_called_once_with()


# @pytest.mark.sdpmln
# @pytest.mark.parametrize(
#     "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
# )
# def test_on_command_fail_sdp_master(tango_context, sdp_master_device):
#     cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
#     adapter_factory = HelperAdapterFactory()
#     cm.sdp_master_dev_name = sdp_master_device
#     # include exception in On command
#     adapter_factory.get_or_create_adapter(
#         sdp_master_device, attrs={"On.side_effect": Exception}
#     )
#     on_command = On(cm, cm.op_state_model, adapter_factory)
#     assert on_command.check_allowed()
#     (result_code, message) = on_command.do()
#     assert result_code == ResultCode.FAILED
#     assert sdp_master_device in message


# @pytest.mark.parametrize(
#     "sdp_master_device", [SDP_MASTER_DEVICE_MID, SDP_MASTER_DEVICE_LOW]
# )
# def test_on_command_is_not_allowed_device_unresponsive(
#     tango_context, sdp_master_device
# ):
#     cm, _ = create_cm("SdpMLNComponentManager", sdp_master_device)
#     cm._device = DeviceInfo(sdp_master_device, _unresponsive=True)
#     pytest.raises(DeviceUnresponsive)
