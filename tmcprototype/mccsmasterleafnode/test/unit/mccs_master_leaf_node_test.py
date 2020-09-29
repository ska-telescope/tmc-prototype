#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the MccsMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #

# Standard Python imports
import contextlib
import importlib
import types
import sys
import mock
from mock import Mock, MagicMock

# Tango imports
import pytest
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from mccsmasterleafnode import MccsMasterLeafNode, const, release
from ska.base.control_model import HealthState
from ska.base.control_model import LoggingLevel

# PROTECTED REGION END #    //  MccsMasterLeafNode imports


@pytest.fixture(scope="function")
def mock_mccs_master():
    mccs_master_fqdn = 'low_mccs/elt/master'
    dut_properties = {'MccsMasterFQDN': mccs_master_fqdn}
    event_subscription_map = {}
    mccs_master_proxy_mock = Mock()
    mccs_master_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
            **kwargs: event_subscription_map.update({attr_name: callback}))
    proxies_to_mock = {mccs_master_fqdn: mccs_master_proxy_mock}
    with fake_tango_system(MccsMasterLeafNode, initial_dut_properties=dut_properties,
                        proxies_to_mock=proxies_to_mock) as tango_context:
        yield mccs_master_proxy_mock, tango_context.device, mccs_master_fqdn, event_subscription_map

@pytest.fixture(scope="function")
def event_subscription(mock_mccs_master):
    event_subscription_map = {}
    mock_mccs_master[0].command_inout_asynch.side_effect = (
        lambda command_name, arg, callback, *args,
            **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def event_subscription_without_arg(mock_mccs_master):
    event_subscription_map = {}
    mock_mccs_master[0].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
            **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(MccsMasterLeafNode) as tango_context:
        yield tango_context


def test_on_should_command_mccs_master_leaf_node_to_start(mock_mccs_master):
# arrange:
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master

    # act:
    device_proxy.On()
    # assert:
    mccs_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON,
                                                                any_method(with_name='on_cmd_ended_cb'))


def test_on_should_command_to_on_with_callback_method(mock_mccs_master, event_subscription_without_arg):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription_without_arg[const.CMD_ON](dummy_event)
    # assert:
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription_without_arg):
# arrange:
    device_proxy=mock_mccs_master[1]

#act
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription_without_arg[const.CMD_ON](dummy_event)
    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


def test_off_should_command_to_off_with_callback_method(mock_mccs_master):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()

    # assert:
    assert device_proxy.activityMessage in const.STR_OFF_CMD_ISSUED


def test_off_should_command_with_callback_method_with_event_error(mock_mccs_master ,event_subscription_without_arg):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription_without_arg[const.CMD_OFF](dummy_event)
    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Event error in Command Callback'
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
                      device_proxy_import_path='tango.DeviceProxy'):
    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()