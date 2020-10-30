#!/usr/bin/env python
import logging
import sys
import pkg_resources

from ska.logging import configure_logging

from tango.server import run
from tango_simlib.tango_sim_generator import configure_device_model, get_tango_device_server


def main():
    sim_data_files = [
        pkg_resources.resource_filename("dishmaster", "dish_master.fgo"),
        pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json"),
    ]

    # add a filter with this device's name
    device_name = f"mid_d{get_instance_name().zfill(4)}/elt/master"
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    # set up Python logging
    configure_logging(tags_filter=TangoDeviceTagsFilter)
    log_name = f"dish-master-{get_instance_name()}"
    logger = logging.getLogger(log_name)
    logger.info("Logging started for %s.", device_name)

    model = configure_device_model(sim_data_files, logger=logger)
    DishMaster, _ = get_tango_device_server(model, sim_data_files)
    run((DishMaster,))


def get_instance_name():
    # Tango device servers are always launched with the instance name as the
    # first argument, so try to return it.
    if len(sys.argv) > 0:
        return sys.argv[1]
    else:
        return "mid_dish_unset"


if __name__ == "__main__":
    main()
