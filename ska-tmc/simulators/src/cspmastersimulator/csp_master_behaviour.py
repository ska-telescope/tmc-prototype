# -*- coding: utf-8 -*-
"""
override class with command handlers for CspMaster.
"""
# Standard python imports
import pkg_resources
import enum
import logging

# Tango import
from tango import DevState, Except, ErrSeverity, Database, DeviceProxy

# SKA imports
from ska_ser_logging import configure_logging
from ska.base.commands import ResultCode


class OverrideCspMaster:
    """Class for csp master simulator device"""

    def action_on(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to ON."""
        model.logger.info("Executing On command")
        _allowed_modes = (DevState.OFF, DevState.STANDBY)
        if tango_dev.get_state() == DevState.ON:
            model.logger.info("CSP master is already in ON state")
            return [[ResultCode.OK], ["CSP master is already in ON state"]]

        if tango_dev.get_state() in _allowed_modes:
            # Turn on CSP Subarrays
            for i in range(1, 4):
                subarray_fqdn = f"mid_csp/elt/subarray_0{i}"
                subarray_dev_proxy = DeviceProxy(subarray_fqdn)
                subarray_dev_proxy.command_inout_asynch(
                    "On", self.command_callback_method(model)
                )
            model.logger.info("On command invoked on Csp Subarray.")

            # set health state
            csp_health_state = model.sim_quantities["healthState"]
            set_enum(csp_health_state, "OK", model.time_func())
            csp_health_state_enum = get_enum_int(csp_health_state, "OK")
            tango_dev.push_change_event("healthState", csp_health_state_enum)
            model.logger.info("heathState transitioned to OK state")

            # Set device state
            tango_dev.set_status("device turned on successfully")
            tango_dev.set_state(DevState.ON)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Csp Master transitioned to the ON state.")
        else:
            Except.throw_exception(
                "ON Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["ON command invoked successfully on simulator."]]

    def command_callback_method(self, model):
        model.logger.info("command callback for async command executed.")

    def action_off(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to OFF."""
        _allowed_modes = (DevState.ON, DevState.ALARM, DevState.STANDBY)
        if tango_dev.get_state() == DevState.OFF:
            model.logger.info("CSP master is already in OFF state")
            return [[ResultCode.OK], ["CSP master is already in Off state"]]

        if tango_dev.get_state() in _allowed_modes:
            # Turn off CSP Subarrays
            for i in range(1, 4):
                subarray_fqdn = f"mid_csp/elt/subarray_0{i}"
                subarray_dev_proxy = DeviceProxy(subarray_fqdn)
                subarray_dev_proxy.command_inout_asynch(
                    "Off", self.command_callback_method(model)
                )
            model.logger.info("Off command invoked on Csp Subarray.")

            # Set device state
            tango_dev.set_status("device turned off successfully")
            tango_dev.set_state(DevState.OFF)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Csp Master transitioned to the OFF state.")

        else:
            Except.throw_exception(
                "Off Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["OFF command invoked successfully on simulator."]]

    def action_cspmasterfault(self, model, tango_dev=None, data_input=None):
        tango_dev.set_state(DevState.FAULT)
        tango_dev.push_change_event("State", tango_dev.get_state())

    def action_reset(self, model, tango_dev=None, data_input=None
    ):
        if tango_dev.get_state() == DevState.FAULT:
            tango_dev.set_state(DevState.OFF)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Reset command successful on simulator.")

    def action_standby(
        self, model, tango_dev=None, data_input=None
    ):  # pylint: disable=W0613
        """Changes the State of the device to STANDBY."""
        _allowed_modes = (DevState.ALARM, DevState.OFF, DevState.ON)
        if tango_dev.get_state() == DevState.STANDBY:
            model.logger.info("CSP master is already in Standby state")
            return [[ResultCode.OK], ["CSP master is already in Standby state"]]

        if tango_dev.get_state() in _allowed_modes:
            # Turn off CSP Subarrays
            for i in range(1, 4):
                subarray_fqdn = f"mid_csp/elt/subarray_0{i}"
                subarray_dev_proxy = DeviceProxy(subarray_fqdn)
                subarray_dev_proxy.command_inout_asynch(
                    "Off", self.command_callback_method(model)
                )
            model.logger.info("Off command invoked on Csp Subarray.")

            # Set device state
            tango_dev.set_status("device turned off successfully")
            tango_dev.set_state(DevState.STANDBY)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Csp Master transitioned to the STANDBY state.")
        else:
            Except.throw_exception(
                "STANDBY Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["STANDBY command invoked successfully on simulator."]]


def get_enum_str(quantity):
    """Returns the enum label of an enumerated data type

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object of a DevEnum attribute
    :return: str
        Current string value of a DevEnum attribute
    """
    EnumClass = enum.IntEnum("EnumLabels", quantity.meta["enum_labels"], start=0)
    return EnumClass(quantity.last_val).name


def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object from model
    :param label: str
        The desired label from enum list
    :param timestamp: float
        The time now
    """
    value = quantity.meta["enum_labels"].index(label)
    quantity.set_val(value, timestamp)


def get_enum_int(quantity, label):
    """Returns the integer index value of an enumerated data type

    :param quantity: tango_simlib.quantities.Quantity
        The quantity object from model
    :param label: str
        The desired label from enum list
    :return: Int
        Current integer value of a DevEnum attribute
    """
    return quantity.meta["enum_labels"].index(label)
