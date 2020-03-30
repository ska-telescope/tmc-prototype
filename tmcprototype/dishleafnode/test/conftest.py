"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""

from __future__ import absolute_import
import importlib
import mock
import pytest
from tango import DeviceProxy, DevFailed
from tango.test_context import DeviceTestContext

@pytest.fixture(scope="class")
def tango_context(request): #, dishmaster_context):
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
    # module = importlib.import_module("{}.{}".format(package_name, module_name))
    # klass = getattr(module, class_name)
    module = importlib.import_module("dishleafnode")
    klass = getattr(module, "DishLeafNode")
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '',
                  'LoggingTargetsDefault': 'console::cout',
                  'LoggingLevelDefault': '4','DishMasterFQDN': "mid_d0001/elt/master", 'TrackDuration': 1,
                  }
    tango_context_dishln = DeviceTestContext(klass, properties=properties, process=False)
    tango_context_dishln.start()
    klass.get_name = mock.Mock(side_effect=tango_context_dishln.get_device_access)
    yield tango_context_dishln
    tango_context_dishln.stop()

@pytest.fixture(scope="class")
def initialize_device(tango_context_init):
    """Re-initializes the device.
    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context_init.device.Init()

@pytest.fixture(scope="class")
def create_dish_proxy():
    dish_proxy = DeviceProxy("mid_d0001/elt/master")
    return dish_proxy