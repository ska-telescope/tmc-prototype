"""Contain the tests for the DishMaster Simulator."""
from tango import DevState


class TestDishMaster(object):
    def test_device_state(self, tango_context):
        assert tango_context.device.State() == DevState.ON

    def test_device_mode_transition(self, tango_context):
        tango_context.device.SetStandbyFPMode()
        assert str(tango_context.device.dishMode) == "dishMode.STANDBY-FP"
