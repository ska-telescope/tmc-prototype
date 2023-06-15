# TODO : Will get Uncommented after refactoring for command is done.
# import time

# import mock
# import pytest
# from ska_tango_base.commands import ResultCode
# from ska_tango_base.control_model import ObsState
# from ska_tmc_common.exceptions import DeviceUnresponsive, InvalidObsStateError
# from ska_tmc_common.test_helpers.helper_adapter_factory import (
#     HelperAdapterFactory,
# )

# from ska_tmc_sdpsubarrayleafnode.commands import Restart
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
# def test_telescope_restart_command(tango_context, devices):
#     logger.info("%s", tango_context)
#     cm, restart_command, my_adapter_factory = get_sdpsln_command_obj(
#         Restart, devices, obsstate_value=ObsState.ABORTED
#     )
#     assert restart_command.check_allowed()
#     (result_code, _) = restart_command.do()
#     assert result_code == ResultCode.OK
#     cm.get_device().obs_state == ObsState.EMPTY
#     adapter = my_adapter_factory.get_or_create_adapter(devices)
#     adapter.proxy.Restart.assert_called()


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_restart_command_fail_subarray(tango_context, devices):
#     logger.info("%s", tango_context)
#     cm, start_time = create_cm("SdpSLNComponentManager", devices)
#     elapsed_time = time.time() - start_time
#     logger.info(
#         "checked %s device in %s", cm.get_device().dev_name, elapsed_time
#     )

#     adapter_factory = HelperAdapterFactory()

#     attrs = {"fetch_skuid.return_value": 123}
#     skuid = mock.Mock(**attrs)

#     # include exception in ObsReset command
#     attrs = {"Restart.side_effect": Exception}
#     subarrayMock = mock.Mock(**attrs)
#     adapter_factory.get_or_create_adapter(devices, proxy=subarrayMock)

#     restart_command = Restart(cm, cm.op_state_model, adapter_factory, skuid)
#     cm.update_device_obs_state(ObsState.ABORTED)
#     assert restart_command.check_allowed()
#     (result_code, message) = restart_command.do()
#     assert result_code == ResultCode.FAILED
#     assert devices in message


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_restart_fail_check_allowed_with_invalid_obsState(
#     tango_context, devices
# ):

#     logger.info("%s", tango_context)
#     _, restart_command, _ = get_sdpsln_command_obj(
#         Restart, devices, obsstate_value=ObsState.IDLE
#     )
#     with pytest.raises(
#         InvalidObsStateError,
#         match="The current observation state for observation is"
#         + "{}".format(ObsState.IDLE),
#     ):
#         restart_command.check_allowed()


# @pytest.mark.sdpsln
# @pytest.mark.parametrize(
#     "devices", [SDP_SUBARRAY_DEVICE_MID, SDP_SUBARRAY_DEVICE_LOW]
# )
# def test_restart_fail_check_allowed_with_device_unresponsive(
#     tango_context, devices
# ):

#     logger.info("%s", tango_context)
#     cm, restart_command, _ = get_sdpsln_command_obj(
#         Restart, devices, obsstate_value=ObsState.ABORTED
#     )
#     device_info = cm.get_device()
#     device_info.update_unresponsive(True)
#     with pytest.raises(
#         DeviceUnresponsive, match="SDP subarray device is not available"
#     ):
#         restart_command.check_allowed()
