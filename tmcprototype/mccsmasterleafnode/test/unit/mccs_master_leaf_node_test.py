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
import json
import mock
from mock import Mock, MagicMock
from os.path import dirname, join

# Tango imports
import pytest
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from mccsmasterleafnode import MccsMasterLeafNode, const, release
from ska.base.control_model import HealthState, ObsState
from ska.base.control_model import LoggingLevel

# PROTECTED REGION END #    //  MccsMasterLeafNode imports
assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()


assign_invalid_key_file = 'invalid_key_AssignResources.json'
path = join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key = f.read()

@pytest.fixture(scope="function")
def mock_mccs_master():
    mccs_master_fqdn = 'low_mccs/elt/master'
    dut_properties = {'MccsMasterFQDN': mccs_master_fqdn}
    event_subscription_map = {}
    mccs_master_proxy_mock = Mock()
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

def test_assign_resources_should_raise_devfailed_exception(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_with_arg
    device_proxy.On()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert const.ERR_DEVFAILED_MSG in str(df.value)

def test_assign_command_with_callback_method(mock_mccs_master, event_subscription):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    dummy_event = command_callback(const.CMD_ALLOCATE)
    event_subscription[const.CMD_ALLOCATE](dummy_event)
    assert const.STR_INVOKE_SUCCESS in device_proxy.activityMessage

def test_assign_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    dummy_event = command_callback_with_event_error(const.CMD_ALLOCATE)
    event_subscription[const.CMD_ALLOCATE](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ALLOCATE in device_proxy.activityMessage

def test_assign_command_with_callback_method_with_devfailed_error(mock_mccs_master, event_subscription):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription[const.CMD_ALLOCATE](dummy_event)
    assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)

def test_allocate_ended_should_raise_dev_failed_exception_for_invalid_obs_state(mock_mccs_master, event_subscription):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.READY
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(json.dumps(assign_input_file))
    assert const.ERR_RAISED_EXCEPTION in str(df.value)

def test_assign_resource_should_raise_exception_when_key_not_found():
    with fake_tango_system(MccsMasterLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_invalid_key)
        assert const.ERR_RAISED_EXCEPTION in str(df)
   
def test_release_resource_should_command_mccs_master_to_release_all_resources(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    device_proxy.ReleaseResources()
    mccs_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_Release,
                                                                        any_method(
                                                                            with_name='releaseresources_cmd_ended_cb'))
    assert_activity_message(device_proxy, const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

def test_release_resource_should_raise_devfail_exception(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.IDLE
    mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseResources()
    assert const.ERR_RELEASE_ALL_RESOURCES in str(df.value)

def test_releaseresources_command_with_callback_method(mock_mccs_master, event_subscription_without_arg):
    # arrange:
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ReleaseResources()
    dummy_event = command_callback(const.CMD_Release)
    event_subscription_without_arg[const.CMD_Release](dummy_event)
    assert const.STR_COMMAND + const.CMD_Release in device_proxy.activityMessage

def test_releaseresources_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription_without_arg):
    # arrange:
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.IDLE
    device_proxy.ReleaseResources()
    dummy_event = command_callback_with_event_error(const.CMD_Release)
    event_subscription_without_arg[const.CMD_Release](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_Release in device_proxy.activityMessage


def raise_devfailed_with_arg(cmd_name, input_arg1, input_arg2):
    # "This function is called to raise DevFailed exception with arguments."
    tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                cmd_name, tango.ErrSeverity.ERR)

def raise_devfailed_exception(cmd_name, inp_str):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception("MccsMasterLeafNode_CommandFailed", const.ERR_DEVFAILED_MSG,
                                    " ", tango.ErrSeverity.ERR)

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

def command_callback_with_devfailed_exception():
    # "This function is called when command is failed with DevFailed exception."
    tango.Except.throw_exception(const.ERR_DEVFAILED_MSG,
                                const.ERR_CALLBACK_CMD_FAILED, " ", tango.ErrSeverity.ERR)


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


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
