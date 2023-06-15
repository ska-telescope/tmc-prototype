# TODO : Will get Uncommented after refactoring for command is done.
# import time
# from os.path import dirname, join

# import pytest
# from ska_tango_base.commands import ResultCode
# from ska_tango_base.control_model import ObsState
# from ska_tmc_common.dev_factory import DevFactory

# from tests.settings import SLEEP_TIME, TIMEOUT, logger
# from tests.ska_tmc_sdpsubarrayleafnode.integration.common import tear_down


# def get_assign_input_str(path):
#     with open(path, "r") as f:
#         assign_input_str = f.read()
#     return assign_input_str


# def obsreset(
#     tango_context,
#     sdpsaln_name,
#     assign_input_str,
# ):

#     logger.info("%s", tango_context)
#     dev_factory = DevFactory()
#     sdpsal_node = dev_factory.get_device(sdpsaln_name)

#     initial_len = len(sdpsal_node.commandExecuted)
#     (result, unique_id) = sdpsal_node.On()
#     (result, unique_id) = sdpsal_node.AssignResources(assign_input_str)
#     sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")

#     sdp_subarray.SetDirectObsState(ObsState.IDLE)
#     assert sdp_subarray.obsState == ObsState.IDLE
#     time.sleep(SLEEP_TIME)
#     (result, unique_id) = sdpsal_node.Abort()
#     sdp_subarray = dev_factory.get_device("mid-sdp/subarray/01")
#     sdp_subarray.SetDirectObsState(ObsState.ABORTED)
#     assert sdp_subarray.obsState == ObsState.ABORTED
#     time.sleep(SLEEP_TIME)
#     (result, unique_id) = sdpsal_node.ObsReset()

#     assert result[0] == ResultCode.QUEUED
#     start_time = time.time()
#     while len(sdpsal_node.commandExecuted) != initial_len + 4:
#         time.sleep(SLEEP_TIME)
#         elapsed_time = time.time() - start_time
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")

#     for command in sdpsal_node.commandExecuted:
#         if command[0] == unique_id[0]:
#             logger.info("command result: %s", command)
#             assert command[2] == "ResultCode.OK"

#     tear_down(dev_factory, sdp_subarray)


# @pytest.mark.xfail
# @pytest.mark.post_deployment
# @pytest.mark.SKA_mid
# @pytest.mark.parametrize(
#     "sdpsaln_name",
#     [("ska_mid/tm_leaf_node/sdp_subarray01")],
# )
# def test_obsreset_command(
#     tango_context,
#     sdpsaln_name,
# ):
#     return obsreset(
#         tango_context,
#         sdpsaln_name,
#         get_assign_input_str(
#             join(
#                 dirname(__file__), "..", "data", "command_AssignResources.json"
#             )
#         ),
#     )
