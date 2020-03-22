"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import mock
import pytest
import importlib


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
    # module = importlib.import_module("{}.{}".format(package_name, module_name))
    # klass = getattr(module, class_name)
    dishmaster_module = importlib.import_module("{}.{}".format('DishMaster', 'DishMaster'))
    klass = getattr(dishmaster_module, 'DishMaster')
    properties = {'GroupDefinitions': ''}
    tango_context_dishmaster = DeviceTestContext(klass, process=False, properties=properties)
    tango_context_dishmaster.start()
    klass.get_name = mock.Mock(side_effect=tango_context_dishmaster.get_device_access)
    yield tango_context_dishmaster
    tango_context_dishmaster.stop()

@pytest.fixture(scope="class")
def initialize_device(tango_context_init):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context2: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context_init.device.Init()
