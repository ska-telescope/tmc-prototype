# -*- coding: utf-8 -*-
#
# This file is part of the SdpMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# Standard python imports
import pkg_resources
import enum
import logging

# Tango import
from tango import DevState, Except, ErrSeverity, Database, Group, DeviceProxy

from tango_simlib.utilities.helper_module import get_server_name
from tango_simlib.tango_launcher import register_device
from tango_simlib.tango_sim_generator import (
    configure_device_models,
    get_tango_device_server,
)

# SKA imports
from ska_ser_logging import configure_logging
from ska.base.commands import ResultCode


class OverrideCspMaster:
    """Class for sdp master simulator device"""

    def action_on(self, model, tango_dev=None, data_input=None
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
                subarray_dev_proxy.command_inout_asynch("On", self.command_callback_method(model))
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

    def action_off(self, model, tango_dev=None, data_input=None
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
                subarray_dev_proxy.command_inout_asynch("Off", self.command_callback_method(model))
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

    def action_standby(self, model, tango_dev=None, data_input=None
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
                subarray_dev_proxy.command_inout_asynch("Off", self.command_callback_method(model))
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


def get_csp_master_sim(device_name):
    """Create and return the Tango device class for Csp Master device
    :params:
        device_name: String. Name of the Csp master device
    :return: tango.server.Device
    The Tango device class for csp Master
    """
    
    logger_name = f"sdp-master-{device_name}"
    logger = logging.getLogger(logger_name)
    
    ## Register simulator device
    log_msg=f"registering device: {device_name}"
    logger.info(log_msg)
    server_name, instance = get_server_name().split("/")
    log_msg = f"server name: {server_name}, instance {instance}"
    logger.info(log_msg)
    tangodb = Database()
    register_device(device_name, "CspMaster", server_name, instance, tangodb)
    tangodb.put_device_property(device_name, {"polled_attr": ["State", "1000"]})
    
    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "ska_tmc_cspmasterleafnode_mid.cspmastersimulator", "CspMaster.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "ska_tmc_cspmasterleafnode_mid.cspmastersimulator", "csp_master_simDD.json"
        )
    )

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
