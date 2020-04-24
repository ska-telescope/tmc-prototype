import contextlib
import importlib
import sys
import json
import types
import mock
from mock import Mock
import tango
from tango import DevState
from tango.test_context import DeviceTestContext
from cspmasterleafnode import CspMasterLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel
import pytest
import time

def test_activityMessage():
    # arrange:
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = "text"
        assert tango_context.device.activityMessage == "text"

def test_State():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ALARM

def test_Status():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert const.STR_DEV_ALARM in tango_context.device.Status()

def test_loggingLevel():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

def test_loggingTargets():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets

def test_testMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

def test_simulationMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

def test_controlMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

def test_adminMode():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE
        
def test_healthState():
    # arrange
    device_under_test = CspMasterLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK
