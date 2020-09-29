"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
from __future__ import absolute_import
import mock
import pytest
import importlib
from tango import DeviceProxy
from tango.test_context import DeviceTestContext

@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    # TODO: package_name and class_name can be used in future
    # fq_test_class_name = request.cls.__module__
    # fq_test_class_name_details = fq_test_class_name.split(".")
    # package_name = fq_test_class_name_details[1]
    # class_name = module_name = fq_test_class_name_details[1]
    # module = importlib.import_module("{}.{}".format("src","centralnode","central_node_low"))
    module = importlib.import_module("centralnode")
    klass = getattr(module, "CentralNode")
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '',
                  'CentralAlarmHandler': '', 'TMAlarmHandler': '',
                  'LoggingTargetsDefault': 'console::cout',
                  'LoggingLevelDefault': '4',
                  'TMMidSubarrayNodes': 'ska_mid/tm_subarray_node/1', 'NumDishes': '4',
                  'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d',
                  'CspMasterLeafNodeFQDN': 'ska_mid/tm_leaf_node/csp_master',
                  'SdpMasterLeafNodeFQDN': 'ska_mid/tm_leaf_node/sdp_master'
                  }
    tango_context = DeviceTestContext(klass, properties=properties, process=False)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)
    yield tango_context
    tango_context.stop()

@pytest.fixture(scope="function")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()

@pytest.fixture(scope="class")
def create_subarray1_proxy():
    subarray1_proxy = DeviceProxy(const.PROP_DEF_VAL_TM_MID_SA1)
    return subarray1_proxy

@pytest.fixture(scope="class")
def create_subarray2_proxy():
    subarray2_proxy = DeviceProxy(const.PROP_DEF_VAL_TM_MID_SA2)
    return subarray2_proxy

@pytest.fixture(scope="class")
def create_leafNode1_proxy():
    leafNode1_proxy = DeviceProxy(const.PROP_DEF_VAL_LEAF_NODE_PREFIX + "0001")
    return leafNode1_proxy

@pytest.fixture(scope="class")
def create_dish_proxy():
    dish_proxy = DeviceProxy("mid_d0001/elt/master")
    return dish_proxy
