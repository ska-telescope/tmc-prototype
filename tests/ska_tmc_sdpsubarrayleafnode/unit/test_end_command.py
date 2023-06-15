# TODO : Will get Uncommented after refactoring for command is done.
# import time

# import mock
# import pytest
# from ska_tango_base.commands import ResultCode
# from ska_tango_base.control_model import ObsState
# from ska_tmc_common.exceptions import InvalidObsStateError
# from ska_tmc_common.test_helpers.helper_adapter_factory import (
#     HelperAdapterFactory,
# )

# from ska_tmc_sdpsubarrayleafnode.commands import End
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
# def test_telescope_end_command(tango_context, devices):
#     logger.info("%s", tango_context)
#     _, end_command, adapter_factory = get_sdpsln_command_obj(
#         End, devices, obsstate_value=ObsState.READY
#     )

#     assert end_command.check_allowed()
#     (result_code, _) = end_command.do()
#     assert result_code == ResultCode.OK
#     adapter = adapter_factory.get_or_create_adapter(devices)
#     adapter.proxy.End.assert_called()


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_telescope_assign_resources_command_fail_subarray(
#     tango_context, devices
# ):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm("SdpSLNComponentManager", devices)
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s device in %s", cm.get_device().dev_name, elapsed_time
#     )

#     adapter_factory = HelperAdapterFactory()

#     attrs = {"fetch_skuid.return_value": 123}
#     skuid = mock.Mock(**attrs)

#     # include exception in AssignResources command
#     attrs = {"End.side_effect": Exception}
#     subarrayMock = mock.Mock(**attrs)
#     adapter_factory.get_or_create_adapter(devices, proxy=subarrayMock)

#     end_command = End(cm, cm.op_state_model, adapter_factory, skuid)
#     cm.update_device_obs_state(ObsState.READY)
#     assert end_command.check_allowed()
#     (result_code, message) = end_command.do()
#     assert result_code == ResultCode.FAILED
#     assert devices in message


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_telescope_end_command_fail_check_allowed_with_invalid_obsState(
#     tango_context, devices
# ):
#     logger.info("%s", tango_context)
#     _, end_command, _ = get_sdpsln_command_obj(
#         End, devices, obsstate_value=ObsState.IDLE
#     )
#     with pytest.raises(
#         InvalidObsStateError,
#         match="The current observation state for observation is"
#         + "{}".format(ObsState.IDLE),
#     ):
#         end_command.check_allowed()
