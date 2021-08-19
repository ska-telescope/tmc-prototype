# -*- coding: utf-8 -*-
#
# This file is part of the SdpMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# Standard Python imports
import pkg_resources
# import enum
import logging

# Tango imports
from tango import DevState, Except, ErrSeverity, Database, Group

from tango_simlib.utilities.helper_module import get_server_name
from tango_simlib.tango_launcher import register_device
from tango_simlib.tango_sim_generator import (
    configure_device_models, 
    get_tango_device_server
)

# SKA imports
from ska.base.commands import ResultCode
from ska_ser_logging import configure_logging


class OverrideSdpMaster:
    """Class for sdp master simulator device"""

    def action_on(self, model, tango_dev=None, data_input=None
    ): # pylint: disable=W0613
        model.logger.info("Executing On command")
        _allowed_modes = (DevState.OFF, DevState.STANDBY)
        if tango_dev.get_state() == DevState.ON:
            model.logger.info("SDP master is already in ON state")
            return [[ResultCode.OK], ["SDP master is already in ON state"]]

        if tango_dev.get_state() in _allowed_modes:
           
            # set health state
            sdp_health_state = model.sim_quantities["healthState"]
            set_enum(sdp_health_state, "OK", model.time_func())
            sdp_health_state_enum = get_enum_int(sdp_health_state, "OK")
            tango_dev.push_change_event("healthState", sdp_health_state_enum)
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

    def action_off(self, model, tango_dev=None, data_input=None
    ): # pylint: disable=W0613
        _allowed_modes = (DevState.ON, DevState.ALARM, DevState.STANDBY)
        if tango_dev.get_state() == DevState.OFF:
            model.logger.info("SDP master is already in OFF state")
            return [[ResultCode.OK], ["SDP master is already in Off state"]]

        if tango_dev.get_state() in _allowed_modes:
            
            # Set device state
            tango_dev.set_status("device turned off successfully")
            tango_dev.set_state(DevState.OFF)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Sdp Master transitioned to the OFF state.")
    
        else:
            Except.throw_exception(
                "Off Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )
        return [[ResultCode.OK], ["OFF command invoked successfully on simulator."]]
    
    def action_standby(self, model, tango_dev=None, data_input=None
    ): # pylint: disable=W0613
        _allowed_modes = (DevState.ON, DevState.ALARM, DevState.OFF)
        if tango_dev.get_state() == DevState.STANDBY:
            model.logger.info("SDP master is already in STANDBY state")
            return [[ResultCode.OK], ["SDP master is already in STANDBY state"]]

        if tango_dev.get_state() in _allowed_modes:
            # Set device state
            tango_dev.set_status("device turned to STANDBY successfully")
            tango_dev.set_state(DevState.STANDBY)
            tango_dev.push_change_event("State", tango_dev.get_state())
            model.logger.info("Sdp Master transitioned to the STANDBY state.")
       
        else:
            Except.throw_exception(
                "STANDBY Command Failed",
                "Not allowed",
                ErrSeverity.WARN,
            )


def get_sdp_master_sim(device_name):
    """Create and return the Tango device class for Sdp Master device
    :params: 
        device_name: String. Name of the Sdp master device
    :return: tango.server.Device
    The Tango device class for Sdp Master
    """

    logger_name = f"sdp-master-{device_name}"
    logger = logging.getLogger(logger_name)

    logger.info("Registering device: %s.", device_name)
    server_name, instance = get_server_name().split("/")
    logger.info("server name: %s, instance %s",server_name,instance)
    tangodb = Database() 
    register_device(device_name, "SdpMaster", server_name, instance, tangodb)
    tangodb.put_device_property(device_name, {"polled_attr": ["State", "1000"]})

    ## Create Simulator
    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename("ska_tmc_sdpmasterleafnode_mid.simulator", "sdp_master.fgo")
    )
    sim_data_files.append(
        pkg_resources.resource_filename("ska_tmc_sdpmasterleafnode_mid.simulator", "sdp_master_sim_dd.json")
    )
    # add a filter with this device's name
    device_name_tag = f"tango-device:{device_name}"
    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    # set up Python logging
    configure_logging(tags_filter=TangoDeviceTagsFilter)
    logger_name = f"sdp-master-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)
    configure_args = {"logger": logger}
    # test/nodb/sdpmaster is used for testing
    if device_name == "test/nodb/sdpmaster":
        configure_args["test_device_name"] = device_name

    logger.debug("Configuring device model")
    models = configure_device_models(sim_data_files, **configure_args)
    tango_ds = get_tango_device_server(models, sim_data_files)

    return tango_ds[0]

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