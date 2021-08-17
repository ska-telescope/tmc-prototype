import pkg_resources
import logging

from tango_simlib.tango_sim_generator import (
    configure_device_models,
    get_tango_device_server,
)

from ska_ser_logging import configure_logging
from tango import Database
from tango_simlib.utilities.helper_module import get_server_name
from tango_simlib.tango_launcher import register_device, put_device_property


def get_tango_server_class(device_name):
    """Build and return the Tango device class for CspSubarray

    :param device_name: str
        The Tango device name
    :return CspSubarray: tango.server.Device
        The Tango device class for CspSubarray
    """
    # set up Python logging
    logger_name = f"csp-subarray-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)

    ## Register simulator device
    log_msg=f"registering device: {device_name}"
    logger.info(log_msg)
    server_name, instance = get_server_name().split("/")
    log_msg = f"server name: {server_name}, instance {instance}"
    logger.info(log_msg)
    tangodb = Database()
    register_device(device_name, "CspSubarray", server_name, instance, tangodb)

    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "ska_tmc_cspsubarrayleafnode_mid.cspsubarraysimulator", "CspSubarray.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "ska_tmc_cspsubarrayleafnode_mid.cspsubarraysimulator", "csp_subarray_SimDD.json"
        )
    )
    
    # Add a filter with this device name
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    configure_logging(tags_filter=TangoDeviceTagsFilter)    
    
    configure_args = {"logger": logger}
    # test/nodb/cspsubarray is used for testing
    if device_name == "test/nodb/cspsubarray":
        configure_args["test_device_name"] = device_name

    model = configure_device_models(sim_data_files)
    tango_ds = get_tango_device_server(model, sim_data_files)
    return tango_ds
