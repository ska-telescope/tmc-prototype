# -*- coding: utf-8 -*-
"""
override class with command handlers for CspSubarray.
"""
# Standard python imports
import enum
import logging

from collections import namedtuple

# Tango import
from tango import DevState, ObsState, Except, ErrSeverity

# Additional import
from ska.logging import configure_logging

configure_logging()
MODULE_LOGGER = logging.getLogger(__name__)


class OverrideCspSubarray(object):
    
    def action_assign_resources(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("assign_resources is invoked")


    def action_end_scan(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("end_scan is invoked")

    def action_abort(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("abort is invoked")

    def action_release_all_resources(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("release_all_resources is invoked")

    def action_configure(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("configure is invoked")

    def action_scan(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("scan is invoked")

    def action_go_to_idle(self, model, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("go_to_idle is invoked")


def get_enum_str(quantity):
    """Returns the enum label of an enumerated data type

    :param quantity: object
        The quantity object of a DevEnum attribute
    :return: str
        Current string value of a DevEnum attribute
    """
    EnumClass = enum.IntEnum("EnumLabels", quantity.meta["enum_labels"], start=0)
    return EnumClass(quantity.last_val).name


def set_enum(quantity, label, timestamp):
    """Sets the quantity last_val attribute to index of label

    :param quantity: object
        The quantity object from model
    :param label: str
        The desired label from enum list
    :param timestamp: float
        The time now
    """
    value = quantity.meta["enum_labels"].index(label)
    quantity.set_val(value, timestamp)


def get_direction_sign(here, there):
    """Return sign (+1 or -1) required to move from here to there."""
    return 1 if here < there else -1
