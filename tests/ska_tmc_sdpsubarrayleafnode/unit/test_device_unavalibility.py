# import time

# import pytest
# from ska_tmc_common import DevFactory
# from ska_tmc_dishleafnode.dish_leaf_node import DishLeafNode

# from tests.settings import DISH_LEAF_NODE_DEVICE, logger


# @pytest.fixture()
# def devices_to_load():
#     """Returns helper state devices."""
#     return (
#         {
#             "class": DishLeafNode,
#             "devices": [
#                 {"name": "ska_mid/tm_leaf_node/d0001"},
#             ],
#         },
#     )


# @pytest.mark.manu
# def test_check_device_availabillity(tango_context):
#     logger.info(f"{tango_context}")
#     dev_factory = DevFactory()
#     dish_leaf_node = dev_factory.get_device(DISH_LEAF_NODE_DEVICE)
#     time.sleep(1)
#     dish_value = dish_leaf_node.isSubSystemAvailable
#     assert dish_value is False
# -
