import pkg_resources
import logging

from tango_simlib.tango_sim_generator import (
    configure_device_models,
    get_tango_device_server,
)

from ska_ser_logging import configure_logging
from tango import Database
from tango_simlib.utilities.helper_module import get_server_name
from tango_simlib.tango_launcher import register_device

def get_tango_server_class(device_name):
    """Create and return the Tango device class for Csp Master device
    :params:
        device_name: String. Name of the Csp master device
    :return: tango.server.Device
    The Tango device class for csp Master
    """

    logger_name = f"csp-master-{device_name}"
    logger = logging.getLogger(logger_name)

    ## Register simulator device
    logger.info("registering device:%s", device_name)
    server_name, instance = get_server_name().split("/")
    logger.info("server name: %s, instance %s", server_name, instance)
    tangodb = Database()
    register_device(device_name, "CspMaster", server_name, instance, tangodb)
    tangodb.put_device_property(device_name, {"polled_attr": ["State", "1000"]})

    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "cspmastersimulator", "CspMaster.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "cspmastersimulator", "csp_master_SimDD.json"
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

    model = configure_device_models(sim_data_files, **configure_args)
    tango_ds = get_tango_device_server(model, sim_data_files)
    return tango_ds
