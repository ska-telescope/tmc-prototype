#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the MCCSMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
from devicetest import DeviceTestCase, main
from mccsmasterleafnode import MCCSMasterLeafNode



# Note:
#
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing


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
def tango_context():
    with fake_tango_system(MccsMasterLeafNode) as tango_context:
        yield tango_context


def test_on_should_command_mccs_master_leaf_node_to_start(mock_mccs_master):
# arrange:
    mccs_master_proxy_mock, device_proxy, event_subscription_map = mock_mccs_master

    # act:
    device_proxy.On()
    # assert:
    mccs_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON, [],
                                                                any_method(with_name='on_cmd_ended_cb'))


def test_on_should_command_to_on_with_callback_method(mock_mccs_master, event_subscription):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription[const.CMD_ON](dummy_event)
    # assert:
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription):
# arrange:
    device_proxy=mock_mccs_master[1]

#act
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription[const.CMD_ON](dummy_event)
    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage


def test_off_should_command_mccs_master_leaf_node_to_stop(mock_mccs_master):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()
    # assert:
    assert device_proxy.activityMessage in const.STR_OFF_CMD_ISSUED


def test_off_should_command_to_off_with_callback_method(mock_mccs_master):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()

    # assert:
    assert device_proxy.activityMessage in const.STR_OFF_CMD_ISSUED


def test_off_should_command_with_callback_method_with_event_error(mock_mccs_master ,event_subscription):
# arrange:
    device_proxy=mock_mccs_master[1]

    # act:
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription[const.CMD_OFF](dummy_event)
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


@classmethod
def mocking(cls):
    """Mock external libraries."""
    # Example : Mock numpy
    # cls.numpy = MCCSMasterLeafNode.numpy = MagicMock()
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_mocking) ENABLED START #
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_mocking

def test_properties(self):
    # test the properties
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_properties) ENABLED START #
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_properties
    pass

def test_State(self):
    """Test for State"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_State) ENABLED START #
    self.device.State()
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_State

def test_Status(self):
    """Test for Status"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_Status) ENABLED START #
    self.device.Status()
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Status

def test_GetVersionInfo(self):
    """Test for GetVersionInfo"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_GetVersionInfo) ENABLED START #
    self.device.GetVersionInfo()
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_GetVersionInfo

def test_Reset(self):
    """Test for Reset"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_Reset) ENABLED START #
    self.device.Reset()
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Reset

def test_AssignResource(self):
    """Test for AssignResource"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_AssignResource) ENABLED START #
    self.device.AssignResource("")
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_AssignResource

def test_ReleaseResources(self):
    """Test for ReleaseResources"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_ReleaseResources) ENABLED START #
    self.device.ReleaseResources("")
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_ReleaseResources

def test_On(self):
    """Test for On"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_On) ENABLED START #
    self.device.On()
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_On

def test_Off(self):
    """Test for Off"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_Off) ENABLED START #
    self.device.Off()
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Off

def test_buildState(self):
    """Test for buildState"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_buildState) ENABLED START #
    self.device.buildState
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_buildState

def test_versionId(self):
    """Test for versionId"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_versionId) ENABLED START #
    self.device.versionId
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_versionId

def test_loggingLevel(self):
    """Test for loggingLevel"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_loggingLevel) ENABLED START #
    self.device.loggingLevel
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_loggingLevel

def test_healthState(self):
    """Test for healthState"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_healthState) ENABLED START #
    self.device.healthState
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_healthState

def test_adminMode(self):
    """Test for adminMode"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_adminMode) ENABLED START #
    self.device.adminMode
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_adminMode

def test_controlMode(self):
    """Test for controlMode"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_controlMode) ENABLED START #
    self.device.controlMode
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_controlMode

def test_simulationMode(self):
    """Test for simulationMode"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_simulationMode) ENABLED START #
    self.device.simulationMode
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_simulationMode

def test_testMode(self):
    """Test for testMode"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_testMode) ENABLED START #
    self.device.testMode
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_testMode

def test_activitymessage(self):
    """Test for activitymessage"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_activitymessage) ENABLED START #
    self.device.activitymessage
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_activitymessage

def test_loggingTargets(self):
    """Test for loggingTargets"""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_loggingTargets) ENABLED START #
    self.device.loggingTargets
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_loggingTargets


# Main execution
if __name__ == "__main__":
    main()
