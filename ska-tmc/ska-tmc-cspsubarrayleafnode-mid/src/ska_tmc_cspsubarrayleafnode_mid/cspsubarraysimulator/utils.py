import pkg_resources
import logging

from tango_simlib.tango_sim_generator import (
    configure_device_models,
    get_tango_device_server,
)

from ska.logging import configure_logging


def get_tango_server_class(device_name):
    """Build and return the Tango device class for CspSubarray

    :param device_name: str
        The Tango device name
    :return CspSubarray: tango.server.Device
        The Tango device class for CspSubarray
    """
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "cspsubarrayleafnode.cspsubarraysimulator", "CspSubarray.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "cspsubarrayleafnode.cspsubarraysimulator", "csp_subarray_SimDD.json"
        )
    )
    # set up Python logging
    configure_logging(tags_filter=TangoDeviceTagsFilter)
    logger_name = f"csp-subarray-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)
    configure_args = {"logger": logger}
    # test/nodb/cspsubarray is used for testing
    if device_name == "test/nodb/cspsubarray":
        configure_args["test_device_name"] = device_name

    model = configure_device_models(sim_data_files)
    tango_ds = get_tango_device_server(model, sim_data_files)
    return tango_ds
