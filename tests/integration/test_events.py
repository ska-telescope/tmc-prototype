# import time

# import pytest
# import tango
# from ska_tmc_common.dev_factory import DevFactory

# from tests.settings import SLEEP_TIME, TIMEOUT, logger


# def internal_model_events(tango_context, sdpsaln_name):
#     pytest.num_events_arrived = 0

#     def event_callback(evt):
#         assert not evt.err
#         pytest.num_events_arrived += 1

#     logger.info("%s", tango_context)
#     dev_factory = DevFactory()
#     sdpsal_node = dev_factory.get_device(sdpsaln_name)

#     event_id = sdpsal_node.subscribe_event(
#         "lastDeviceInfoChanged",
#         tango.EventType.CHANGE_EVENT,
#         event_callback,
#         stateless=True,
#     )

#     start_time = time.time()
#     while pytest.num_events_arrived <= 1:
#         logger.info("waiting events: %s", pytest.num_events_arrived)
#         time.sleep(SLEEP_TIME)
#         elapsed_time = time.time() - start_time
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")

#     assert pytest.num_events_arrived > 1

#     sdpsal_node.unsubscribe_event(event_id)


# # def command_in_progress_events(tango_context, central_node_name):
# #     pytest.num_events_arrived = 0

# #     def event_callback(evt):
# #         assert not evt.err
# #         pytest.num_events_arrived += 1

# #     logger.info("%s", tango_context)
# #     dev_factory = DevFactory()
# #     central_node = dev_factory.get_device(central_node_name)

# #     event_id = central_node.subscribe_event(
# #         "commandInProgress",
# #         tango.EventType.CHANGE_EVENT,
# #         event_callback,
# #         stateless=True,
# #     )

# #     ensure_checked_devices(central_node)

# #     central_node.On()
# #     central_node.Off()

# #     start_time = time.time()
# #     while pytest.num_events_arrived < 5:
# #         logger.info("waiting events: %s", pytest.num_events_arrived)
# #         time.sleep(SLEEP_TIME)
# #         elapsed_time = time.time() - start_time
# #         if elapsed_time > TIMEOUT:
# #             pytest.fail("Timeout occurred while executing the test")

# #     # None
# #     # TelescopeOn
# #     # None
# #     # TelescopeOff
# #     # None
# #     # totale 5
# #     assert pytest.num_events_arrived == 5

# #     central_node.unsubscribe_event(event_id)


# @pytest.mark.post_deployment
# @pytest.mark.SKA_mid
# def test_internal_model_events_mid(tango_context):
#     internal_model_events(tango_context, "ska_mid/tm_leaf_node/sdp_subarray01")
