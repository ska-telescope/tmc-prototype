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
import logging

# Tango imports
from tango import DevState
from tango_simlib.tango_sim_generator import (configure_device_models, get_tango_device_server)

# SKA imports
from ska.logging import configure_logging

class OverrideSdpMaster():
    """Test class for sdp master simulator device"""

    def action_on(self, model, tango_dev=None, data_input=None):
        model.logger.info("Executing On command")
        tango_dev.set_state(DevState.ON)
        model.sim_quantities["TestAttr"].set_val("On command", model.time_func())
        tango_dev.push_change_event("TestAttr", "test value on")
        tango_dev.set_status("device turned on successfully")

    def action_off(self, model, tango_dev=None, data_input=None):
        model.logger.info("Executing Off command")
        tango_dev.set_state(DevState.OFF)
        model.sim_quantities["TestAttr"].set_val("Off command", model.time_func())
        tango_dev.push_change_event("TestAttr", "test value off")
        tango_dev.set_status("device turned off successfully")


def get_sdp_master_sim(device_name):
    """Create and return the Tango device class for Sdp Master device
    :params: 
        device_name: String. Name of the Sdp master device
    :return: tango.server.Device
    The Tango device class for Sdp Master
    """

    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename("sdpmasterleafnode.simulator", "sdp_master.fgo")
    )
    sim_data_files.append(
        pkg_resources.resource_filename("sdpmasterleafnode.simulator", "sdp_master_sim_dd.json")
    )
    # add a filter with this device's name
    device_name = "mid"
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