# -*- coding: utf-8 -*-
"""
override class with command handlers for CspSubarray.
"""
# Standard python imports
import enum
import logging
import time

from collections import namedtuple

# Tango import
from tango import DevState, Except, ErrSeverity

# Additional import
# from ska.logging import configure_logging

# configure_logging()
MODULE_LOGGER = logging.getLogger(__name__)


class OverrideCspSubarray(object):
    
    def action_assignresources(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("assign_resources is invoked")
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate == "EMPTY"):
            if('subarray_id' in data_input):
                set_enum(obsstate_attribute, "RESOURCING", models.time_func())
                print("obsstate in resourcing ::::::::::::",get_enum_str(obsstate_attribute))

                time.sleep(1)
                set_enum(obsstate_attribute, "IDLE", models.time_func())
                print("obsstate after set to Idle::::::::::::",get_enum_str(obsstate_attribute))

            else:
                Except.throw_exception(
                    "Assign Command Failed",
                    "wrong input arguement.",
                    ErrSeverity.WARN,
                )
        else:
            Except.throw_exception(
                "Assign Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_endscan(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("end_scan is invoked")
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate == "SCANNING"):
            set_enum(obsstate_attribute, "READY", models.time_func())
            print("obsstate in Ready after endscan performed::::::::::",get_enum_str(obsstate_attribute))
            
        else:
            Except.throw_exception(
                "EndScan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        
    def action_abort(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("Abort is invoked")
        _allowed_obsstate = (
            "IDLE",
            "READY",
            "SCANNING",
            "CONFIGURING",
            "RESETTING"
        )
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate in _allowed_obsstate):
           set_enum(obsstate_attribute, "ABORTING", models.time_func())
           print("obsstate in Aborting ::::::::::::",get_enum_str(obsstate_attribute))
           time.sleep(1)
           set_enum(obsstate_attribute, "ABORTED", models.time_func())
           print("obsstate after set to ABORTED::::::::::::",get_enum_str(obsstate_attribute))
            
        else:
            Except.throw_exception(
                "Abort Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_releaseallresources(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("release_all_resources is invoked")
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate == "IDLE"):
            set_enum(obsstate_attribute, "RESOURCING", models.time_func())
            print("obsstate in resourcing ::::::::::::",get_enum_str(obsstate_attribute))

            time.sleep(1)
            set_enum(obsstate_attribute, "EMPTY", models.time_func())
            print("obsstate after set to EMPTY::::::::::::",get_enum_str(obsstate_attribute))
           
        else:
            Except.throw_exception(
                "Release Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_configure(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("configure is invoked")
        _allowed_obsstate = (
            "IDLE",
            "READY"
        )
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate in _allowed_obsstate):
            if('csp' in data_input):
                set_enum(obsstate_attribute, "CONFIGURING", models.time_func())
                print("obsstate in configuring ::::::::::::",get_enum_str(obsstate_attribute))

                time.sleep(1)
                set_enum(obsstate_attribute, "READY", models.time_func())
                print("obsstate after set to Ready::::::::::::",get_enum_str(obsstate_attribute))

                print("Configure command is invoked")
            else:
                Except.throw_exception(
                    "Configure Command Failed",
                    "wrong input arguement.",
                    ErrSeverity.WARN,
                )
        else:
            Except.throw_exception(
                "Configure Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_scan(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("Scan is invoked")
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate == "READY"):
            if('scan_id' in data_input):
                set_enum(obsstate_attribute, "SCANNING", models.time_func())
                print("obsstate in SCANNING ::::::::::::",get_enum_str(obsstate_attribute))

                time.sleep(10)
                set_enum(obsstate_attribute, "READY", models.time_func())
                print("obsstate after set to Ready::::::::::::",get_enum_str(obsstate_attribute))

                print("Scan command is invoked")
            else:
                Except.throw_exception(
                    "Scan Command Failed",
                    "wrong input arguement.",
                    ErrSeverity.WARN,
                )
        else:
            Except.throw_exception(
                "Scan Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )
        

    def action_gotoidle(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("go_to_idle is invoked")
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate == "READY"):
            set_enum(obsstate_attribute, "IDLE", models.time_func())
            print("obsstate in IDLE after gotoidle performed::::::::::",get_enum_str(obsstate_attribute))
            
        else:
            Except.throw_exception(
                "gotoidle Command Failed",
                "Not allowed in current Obstate.",
                ErrSeverity.WARN,
            )

    def action_reset(self, models, tango_dev=None, data_input=None):
        """Changes the State of the device to .
        """
        print("Reset is invoked")
        obsstate_attribute = models.sim_quantities['obsState']
        obsstate = get_enum_str(obsstate_attribute)
        print("obsstate::::::::::::",obsstate)
        if (obsstate == "ABORTED"):
            set_enum(obsstate_attribute, "EMPTY", models.time_func())
            print("obsstate INITIATION performed::::::::::",get_enum_str(obsstate_attribute))
            
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
        The quantity object from models
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
