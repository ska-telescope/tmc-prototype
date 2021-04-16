"""Contain the tests for the DishMaster Simulator."""
from tango import DevState
import pytest


class TestDishMaster(object):
    @pytest.mark.xfail
    def test_device_state(self, tango_context):
        assert tango_context.device.State() == DevState.STANDBY

    @pytest.mark.xfail
    def test_device_mode_transition(self, tango_context):
        tango_context.device.SetStandbyFPMode()
        assert str(tango_context.device.dishMode) == "dishMode.STANDBY_FP"
        assert tango_context.device.State() == DevState.STANDBY
