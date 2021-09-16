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
    logger.info("registering device: %s", device_name)
    server_name, instance = get_server_name().split("/")
    logger.info("server name: %s, instance %s", server_name, instance)
    tangodb = Database()
    register_device(device_name, "SdpSubarray", server_name, instance, tangodb)
    polling_attribute = {"polled_attr": ["receiveAddresses", "10000"]}
    tangodb.put_device_property(device_name, polling_attribute)
    logger.info("attribute polled on sdp subarray.")

    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "sdpsubarraysimulator", "SdpSubarray.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "sdpsubarraysimulator",
            "sdp_subarray_SimDD.json",
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
