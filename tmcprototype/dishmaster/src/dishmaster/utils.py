import pkg_resources
import logging
import sys

from tango_simlib.tango_sim_generator import configure_device_model, get_tango_device_server
from ska.logging import configure_logging


def get_tango_server_class(device_name):
    """Build and return the Tango device class for DishMaster

    Parameters
    ----------
    device_name: string
        The Tango device name

    Returns
    -------
    DishMaster: tango.server.Device
        The Tango device class for dishmaster
    """
    data_descr_files = []
    data_descr_files.append(pkg_resources.resource_filename("dishmaster", "dish_master.fgo"))
    data_descr_files.append(pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json"))

    # add a filter with this device's name
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    # set up Python logging
    configure_logging(tags_filter=TangoDeviceTagsFilter)
    logger_name = f"dish-master-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)
    configure_args = {"logger": logger}
    # test/nodb/dishmaster is used for testing
    if device_name == "test/nodb/dishmaster":
        configure_args["test_device_name"] = device_name
    model = configure_device_model(data_descr_files, **configure_args)
    DishMaster, _ = get_tango_device_server(model, data_descr_files)
    return DishMaster
