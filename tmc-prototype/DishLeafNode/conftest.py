"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""


import mock
import pytest
import importlib

from PyTango._PyTango import DeviceProxy
from tango.test_context import DeviceTestContext

# @pytest.fixture(scope="class")
# def dishmaster_context():
#     """Creates and returns a TANGO DeviceTestContext object.
#     Parameters
#     ----------
#     request: _pytest.fixtures.SubRequest
#         A request object gives access to the requesting test context.
#     """
#     ###########################
#     dishmaster_module = importlib.import_module("{}.{}".format('DishMaster', 'DishMaster'))
#     dishmaster_klass = getattr(dishmaster_module, 'DishMaster')
#     dishmaster_context = DeviceTestContext(dishmaster_klass , process= True) #, device_name="mid_d0001/elt/master")
#     ##########################
#     dishmaster_context.start()
#     dishmaster_klass.get_name = mock.Mock(side_effect=dishmaster_context.get_device_access)
#     print "In dishMaster context", dishmaster_context.device_name
#     print "Host and Port name are: ", dishmaster_context.host, dishmaster_context.port
#     yield dishmaster_context
#     #dishmaster_context.stop()



@pytest.fixture(scope="class")
def tango_context(request): #, dishmaster_context):
    """Creates and returns a TANGO DeviceTestContext object.
    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    print "request is:", request
    print "request.cls is:", request.cls
    fq_test_class_name = request.cls.__module__
    print "class name is:", fq_test_class_name
    fq_test_class_name_details = fq_test_class_name.split(".")
    print "class details are:", fq_test_class_name_details 
    package_name = fq_test_class_name_details[0]
    print "package name is:", package_name
    class_name = module_name = fq_test_class_name_details[0]
    print "module and class name are :", class_name, module_name
    module = importlib.import_module("{}.{}".format(package_name, module_name))
    print "module name is:", module
    klass = getattr(module, class_name)
    print "klass is:", klass
    # "tango://apurva-pc:10000/
    #dishmaster_fqdn =  "tango://"+ str(dishmaster_context.host) +  ":" + str(10000) + "/" + 'mid_d0001/elt/master'
    #dishmaster_fqdn = dishmaster_context.get_device_access()
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '', 'CentralLoggingTarget': '',
                  'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost',
                  'DishMasterFQDN': "tango://apurva-pc:10000/mid_d0001/elt/master", #dishmaster_fqdn,
                  }

    print "In tango_context", properties['DishMasterFQDN']
    tango_context = DeviceTestContext(klass, properties=properties, process= False)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)
    yield tango_context
    #dishmaster_context.stop()
    tango_context.stop()



@pytest.fixture(scope="class")
def initialize_device(tango_context):
    """Re-initializes the device.
    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    print "In init device function"
    yield tango_context.device.Init()

@pytest.fixture(scope="class")
def create_dish_proxy(): #dishmaster_context):
    dish_proxy = DeviceProxy("tango://apurva-pc:10000/mid_d0001/elt/master")  #(dishmaster_context.get_device_access())
    return dish_proxy