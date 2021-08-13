import pkg_resources
import logging
from tango import Database
from ska_ser_logging import configure_logging
from tango_simlib.utilities.helper_module import get_server_name
from tango_simlib.tango_launcher import register_device
from tango_simlib.tango_sim_generator import (
    configure_device_models,
    get_tango_device_server,
)

def get_tango_server_class(device_name):
    """Build and return the Tango device class for SdpSubarray

    :param device_name: str
        The Tango device name
    :return SdpSubarray: tango.server.Device
        The Tango device class for SdpSubarray
    """

    # set up Python logging
    logger_name = f"sdp-subarray-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)

    ## Register simulator device
    log_msg=f"registering device: {device_name}"
    logger.info(log_msg)
    server_name, instance = get_server_name().split("/")
    log_msg = f"server name: {server_name}, instance {instance}"
    logger.info(log_msg)
    register_device(device_name, "SdpSubarray", server_name, instance, Database())
    

    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "ska_tmc_sdpsubarrayleafnode_mid.sdpsubarraysimulator", "SdpSubarray.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "ska_tmc_sdpsubarrayleafnode_mid.sdpsubarraysimulator", "sdp_subarray_SimDD.json"
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
    # test/nodb/sdpsubarray is used for testing
    if device_name == "test/nodb/sdpsubarray":
        configure_args["test_device_name"] = device_name

    model = configure_device_models(sim_data_files)
    tango_ds = get_tango_device_server(model, sim_data_files)
    return tango_ds
