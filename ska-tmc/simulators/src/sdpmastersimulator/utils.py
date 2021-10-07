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
    logger.info("server name: %s, instance %s", server_name, instance)
    tangodb = Database()
    register_device(device_name, "SdpMaster", server_name, instance, tangodb)
    tangodb.put_device_property(device_name, {"polled_attr": ["State", "1000"]})

    ## Create Simulator
    sim_data_files = []
    sim_data_files.append(
        pkg_resources.resource_filename(
            "sdpmastersimulator", "SdpMaster.fgo"
        )
    )
    sim_data_files.append(
        pkg_resources.resource_filename(
            "sdpmastersimulator", "sdp_master_SimDD.json"
        )
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
        
    model = configure_device_models(sim_data_files, **configure_args)
    tango_ds = get_tango_device_server(model, sim_data_files)

    return tango_ds