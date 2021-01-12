"""
A module defining pytest fixtures for testing with MultiDeviceTestContext
Requires pytest and pytest-mock
"""
import socket
from unittest import mock

import pytest
import tango

from tango.test_context import MultiDeviceTestContext, get_host_ip


@pytest.fixture(scope="module")
def devices_info(request):
    yield getattr(request.module, "devices_info")


@pytest.fixture(scope="function")
def tango_context(mocker, devices_info):  # pylint: disable=redefined-outer-name
    """
    Creates and returns a TANGO MultiDeviceTestContext object, with
    tango.DeviceProxy patched to work around a name-resolving issue.
    """

    def _get_open_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    HOST = get_host_ip()
    PORT = _get_open_port()

    _DeviceProxy = tango.DeviceProxy

    command_modules = [
        "abort_command",
        "configure_command",
        "endscan_command",
        "restart_command",
        "scan_command",
        "setoperatemode_command",
        "setstandbyfpmode_command",
        "setstandbylpmode_command",
        "setstowmode_command",
        "slew_command",
        "startcapture_command",
        "stopcapture_command",
        "stoptrack_command",
        "track_command",
    ]

    for command_module in command_modules:
        mocker.patch(
            f"dishleafnode.{command_module}.DeviceProxy",
            wraps=lambda fqdn, *args, **kwargs: _DeviceProxy(
                f"tango://{HOST}:{PORT}/{fqdn}#dbase=no"
            ),
        )

    # In tango_simlib devices the Tango DB file is retrieved from the commandline arguments in
    # the function `get_database`.
    # In the test case here, the commandline arguments are `pytest arg 1 arg 2 ...` and
    # does not include `-file`
    # We need to know what the temporary DB filename is before we can mock out the `get_database`
    # function. The DB file is created on init and we need to patch it before the __enter__,
    # thus we manually call the __enter__ and __exit__ of MultiDeviceTestContext.
    context = MultiDeviceTestContext(devices_info, host=HOST, port=PORT, process=True, daemon=False)
    with mock.patch(
        "tango_simlib.utilities.helper_module.get_database", return_value=tango.Database(context.db)
    ):
        context.__enter__()
        yield context
        context.__exit__(None, None, None)
