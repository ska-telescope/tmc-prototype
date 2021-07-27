# -*- coding: utf-8 -*-
"""
override class with command handlers for csp master.
"""
# Standard python imports
import pkg_resources
import enum
import logging

from collections import namedtuple

# Tango import
from tango import DevState, Except, ErrSeverity
from ska.logging import configure_logging
from tango_simlib.tango_sim_generator import (configure_device_models, get_tango_device_server)

class OverrideCspMaster():

    def action_on(self, model, tango_dev=None, data_input=[]):
        """Changes the State of the device to ON.
        """
        model.logger.info("Executing On command")
        _allowed_modes = (
            "OFF",
            "STANDBY"
        )
        if tango_dev.get_state() == DevState.ON:
            model.logger.info("CSP master is already in ON state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.ON)
            model.logger.info("Csp Master transitioned to the ON state.")
            csp_health_state = model.sim_quantities["healthState"]
            set_enum(csp_health_state, "OK", model.time_func())
            tango_dev.push_change_event("healthState", 1)
            tango_dev.set_status("device turned On successfully")
            model.logger.info("heathState transitioned to OK state")
        else:
            Except.throw_exception(
                "ON Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
                )

    def action_off(self, model, tango_dev=None, data_input=[]):
        """Changes the State of the device to OFF.
        """
        _allowed_modes = (
            "ON",
            "ALARM",
            "STANDBY"
        )
        if tango_dev.get_state() == DevState.OFF:
            model.logger.info("CSP master is already in OFF state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.OFF)
            model.logger.info("Csp Master transitioned to the OFF state.")
            csp_health_state = model.sim_quantities["healthState"]
            set_enum(csp_health_state, "OK", model.time_func())
            tango_dev.push_change_event("healthState", 1)
            tango_dev.set_status("device turned off successfully")
            model.logger.info("heathState transitioned to OK state")

        else:
            Except.throw_exception(
                "Off Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
                )

    def action_standby(self, model, tango_dev=None, data_input=[]):
        """Changes the State of the device to STANDBY.
        """
        _allowed_modes = (
            "ON",
            "ALARM",
            "OFF"
        )
        if tango_dev.get_state() == DevState.STANDBY:
            model.logger.info("CSP master is already in OK state")
            return

        if str(tango_dev.get_state()) in _allowed_modes:
            tango_dev.set_state(DevState.STANDBY)
            csp_health_state = model.sim_quantities["healthState"]
            set_enum(csp_health_state, "OK", model.time_func())
            tango_dev.push_change_event("healthState", 1)
            tango_dev.set_status("invoked Standby successfully")
            model.logger.info("heathState transitioned to OK state")
        else:
            Except.throw_exception(
                "STANDBY Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
                )

def get_csp_master_sim(device_name):
    """Create and return the Tango device class for Csp Master device
    :params: 
        device_name: String. Name of the Csp master device
    :return: tango.server.Device
    The Tango device class for csp Master
    """
    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename("cspmasterleafnode.cspmastersimulator", "CspMaster.fgo")
    )
    sim_data_files.append(
        pkg_resources.resource_filename("cspmasterleafnode.cspmastersimulator", "csp_master_simDD.json")
    )

    device_name = "mid_csp/elt/master"
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    # set up Python logging
    configure_logging(tags_filter=TangoDeviceTagsFilter)
    logger_name = f"csp-master-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)
    configure_args = {"logger": logger}
    # test/nodb/cspmaster is used for testing
    if device_name == "test/nodb/cspmaster":
        configure_args["test_device_name"] = device_name

    logger.debug("Configuring device model")
    
    model = configure_device_models(sim_data_files, **configure_args)
    tango_device_servers = get_tango_device_server(model, sim_data_files)
    return tango_device_servers[0]


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
