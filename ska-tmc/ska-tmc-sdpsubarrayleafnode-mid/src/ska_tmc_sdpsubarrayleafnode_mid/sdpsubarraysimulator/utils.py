import pkg_resources
import logging

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
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

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
    # set up Python logging
    logger_name = f"sdp-subarray-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)
    configure_args = {"logger": logger}
    # test/nodb/sdpsubarray is used for testing
    if device_name == "test/nodb/sdpsubarray":
        configure_args["test_device_name"] = device_name

    model = configure_device_models(sim_data_files)
    tango_ds = get_tango_device_server(model, sim_data_files)
    return tango_ds
