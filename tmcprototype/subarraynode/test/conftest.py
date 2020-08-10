"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import importlib
import mock
import pytest
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
    # module = importlib.import_module("{}.{}".format(package_name, module_name))
    # klass = getattr(module, class_name)
    properties = {'CspSubarrayLNFQDN': 'ska_mid/tm_leaf_node/csp_subarray01',
                  'SdpSubarrayLNFQDN': 'ska_mid/tm_leaf_node/sdp_subarray01',
                  'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d',
                  'SdpSubarrayFQDN': 'mid_sdp/elt/subarray_1',
                  'CspSubarrayFQDN': 'mid_csp/elt/subarray_01'}
    module = importlib.import_module("subarraynode")
    klass = getattr(module, "SubarrayNode")
    tango_context = DeviceTestContext(klass, properties=properties)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)
    yield tango_context
    tango_context.stop()


@pytest.fixture(scope="class")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()


@pytest.fixture(scope="class")
def create_centralnode_proxy():
    centralnode_proxy = DeviceProxy("ska_mid/tm_central/central_node")
    return centralnode_proxy


@pytest.fixture(scope="class")
def create_cspmasterln_proxy():
    cspmasterln_proxy = DeviceProxy("ska_mid/tm_leaf_node/csp_master")
    return cspmasterln_proxy


@pytest.fixture(scope="class")
def create_cspsa_proxy():
    cspsa_proxy = DeviceProxy("mid_csp/elt/subarray_01")
    return cspsa_proxy


@pytest.fixture(scope="class")
def create_dish_proxy():
    dish_proxy = DeviceProxy("mid_d0001/elt/master")
    return dish_proxy


@pytest.fixture(scope="class")
def create_dishln_proxy():
    dishln_proxy = DeviceProxy("ska_mid/tm_leaf_node/d0001")
    return dishln_proxy


class StateMachineTester:
    """
    Abstract base class for a class for testing state machines
    """

    def test_state_machine(
            self, machine, state_under_test, action_under_test, expected_state,
    ):
        """
        Implements the unit test for a state machine: for a given
        initial state and an action, does execution of that action, from
        that state, yield the expected results? If the action was
        allowed from that state, does the machine transition to the
        correct state? If the action was not allowed from that state,
        does the machine reject the action (e.g. raise an exception or
        return an error code) and remain in the current state?

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state_under_test: the state from which the
            `action_under_test` is being tested
        :type state_under_test: string
        :param action_under_test: the action being tested from the
            `state_under_test`
        :type action_under_test: string
        :param expected_state: the state to which the machine is
            expected to transition, as a result of performing the
            `action_under_test` in the `state_under_test`. If None, then
            the action should be disallowed and result in no change of
            state.
        :type expected_state: string

        """
        # Put the device into the state under test
        self.to_state(machine, state_under_test)

        # Check that we are in the state under test
        self.assert_state(machine, state_under_test)

        # Test that the action under test does what we expect it to
        if expected_state is None:
            # Action should fail and the state should not change
            self.check_action_disallowed(machine, action_under_test)
            self.assert_state(machine, state_under_test)
        else:
            # Action should succeed
            self.perform_action(machine, action_under_test)
            self.assert_state(machine, expected_state)

    def assert_state(self, machine, state):
        """
        Abstract method for asserting the current state of the state
        machine under test

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: string
        """
        raise NotImplementedError()

    def perform_action(self, machine, action):
        """
        Abstract method for performing an action on the state machine

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def check_action_disallowed(self, machine, action):
        """
        Abstract method for asserting that an action fails if performed
        on the state machine under test in its current state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def to_state(self, machine, target_state):
        """
        Abstract method for getting the state machine into a target
        state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param target_state: the state that we want to get the state
            machine under test into
        :type target_state: str
        """
        raise NotImplementedError()


def load_data(name):
    """
    Loads a dataset by name. This implementation uses the name to find a
    JSON file containing the data to be loaded.

    :param name: name of the dataset to be loaded; this implementation
        uses the name to find a JSON file containing the data to be
        loaded.
    :type name: string
    """
    with open(f"tests/data/{name}.json", "r") as json_file:
        return json.load(json_file)
