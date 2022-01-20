# pylint: disable=unused-argument
import logging
from queue import Empty, Queue
import pytest
from tango import EventType
import tango
from ska_tmc_common.dev_factory import DevFactory
from tango.test_context import MultiDeviceTestContext

from tests.helpers.helper_subarray_device import HelperSubArrayDevice


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": "mid_sdp/elt/subarray_01"},
            ],
        },
    )


@pytest.fixture
def tango_context(devices_to_load, request):
    true_context = request.config.getoption("--true-context")
    logging.info("true context: %s", true_context)
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None


@pytest.fixture(scope="function")
def tango_change_event_helper(device_under_test):
    """
    Return a helper for testing tango change events.

    To use it, call the subscribe method with the name of the attribute
    for which you want change events. The returned value will be a
    callback handler that you can interrogate with
    ``assert_not_called``, ``assert_call``, ``assert_calls``, and
    ``value`` methods.

    .. code-block:: py

        state_callback = tango_change_event_helper.subscribe("state")
        state_callback.assert_call(DevState.OFF)

        # Check that we can't turn off a device that isn't on
        with pytest.raises(DevFailed):
            device_under_test.Off()
        state_callback.assert_not_called()

        # Now turn it on and check that we can turn it off
        device_under_test.On()
        state_callback.assert_call(DevState.ON)

        # Or we can test a sequence of events
        device_under_test.Off()
        device_under_test.On()
        state_callback.assert_calls([DevState.OFF, DevState.ON])

    :param device_under_test: a :py:class:`tango.DeviceProxy` to the
        device under test, running in a
        :py:class:`tango.test_context.DeviceTestContext`.
    :type device_under_test: :py:class:`tango.DeviceProxy`
    """

    class _Callback:
        """
        Private callback handler class.

        An instance is returned by the tango_change_event_helper each
        time it is used to subscribe to a change event.
        """

        @staticmethod
        def subscribe(attribute_name):
            """
            Return an instance that is subscribed to change events on a named attribute.

            :param attribute_name: name of the attribute for which
                change events will be subscribed
            :type attribute_name: str
            :return: an event subscriber helper object
            :rtype: object
            """
            return _Callback(attribute_name)

        def __init__(self, attribute_name):
            """
            Initialise a new instance.

            The instance will be subscribed to change events on the
            named attribute.

            :param attribute_name: name of the attribute for which
                change events will be subscribed
            :type attribute_name: str
            """
            self._value = None
            self._values_queue = Queue()
            self._errors = []
            self._attribute_name = attribute_name

            # Subscription will result in an immediate
            # synchronous callback with the current value,
            # so keep this as the last step in __init__.
            self._id = device_under_test.subscribe_event(
                attribute_name, EventType.CHANGE_EVENT, self
            )

        def __del__(self):
            """Unsubscribe from events before object is destroyed."""
            if hasattr(self, "_id"):
                device_under_test.unsubscribe_event(self._id)

        def __call__(self, event_data):
            """
            Event subscription callback.

            :param event_data: data about the change events
            :type event_data: :py:class:`tango.EventData`
            """
            if event_data.err:
                error = event_data.errors[0]
                self._errors.append(
                    "Event callback error: [%s] %s" % (error.reason, error.desc)
                )
            else:
                self._values_queue.put(event_data.attr_value.value)

        def _next(self):
            """
            Get the attribute value from the next event.

            A value is returned if there is already one,  or if it
            arrives in time.

            :return: the attribute value reported in next change event,
                or None if there is no event
            :rtype: same as attribute type
            """
            assert not self._errors, f"Some errors: {self._errors}"
            try:
                return self._values_queue.get(timeout=1.5)
            except Empty:
                return None

        def assert_not_called(self):
            """
            Assert that there are no new callbacks calls.

            (That is, there are no callback calls that have not already
            been consumed by an ``assert_call`` or ``assert_calls``.)
            """
            assert self._values_queue.empty()

        def assert_call(self, value):
            """
            Assert a call that has been made on this callback.

            Specifically, asserts that this callback has been called
            with a change event that updates the attribute value to a
            given value.

            Note that this method consumes a single event, but may leave
            other events unconsumed.

            :param value: the value that the attribute is asserted to
                have been changed to
            :type value: same as the attribute type
            """
            assert self._next() == value

        def assert_calls(self, values):
            """
            Assert a sequence of calls that have been made on this callback.

            Specifically, assert that this callback has been called with
            a sequence of change events that update the attribute values
            to the given sequence of values.

            Note that this method consumes the events associated with
            the given values, but may leave subsequent events
            unconsumed.

            :param values: sequence of values that the attribute
                is asserted to have been changed to
            :type values: list
            """
            for value in values:
                self.assert_call(value)

        def wait_for_lrc_id(self, unique_id: str):
            """
            Wait for longRunningCommandResult unique ID to be the same as the parameter.

            :param unique_id: The long running command unique ID
            :type unique_id: str
            """
            assert (
                self._attribute_name == "longRunningCommandResult"
            ), "Method only available for longRunningCommandResult"
            while True:
                next_val = self._next()
                assert next_val, "No more events"
                if unique_id == next_val[0]:
                    break

    yield _Callback
