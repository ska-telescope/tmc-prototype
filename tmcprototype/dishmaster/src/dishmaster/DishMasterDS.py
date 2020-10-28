#!/usr/bin/env python
import logging
import sys
import pkg_resources

from ska.logging import configure_logging

from tango.server import server_run
from tango_simlib.tango_sim_generator import (configure_device_model, get_tango_device_server)


def main():
    sim_data_files = [
        pkg_resources.resource_filename('dishmaster', 'dish_master.fgo'),
        pkg_resources.resource_filename('dishmaster', 'dish_master_SimDD.json')
    ]
    
    # set up Python logging
    configure_logging()
    log_name = 'dish-master.{}'.format(get_instance_name())
    logger = logging.getLogger(log_name)
    logger.info("Logging started for DishMaster application")

    # add a filter with this device's name
    device_name_tag = "tango-device:mid_d00{}/elt/master".format(get_instance_name())

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    logger.addFilter(TangoDeviceTagsFilter())

    model = configure_device_model(sim_data_files, logger=logger)
    TangoDeviceServers = get_tango_device_server(model, sim_data_files)
    server_run(TangoDeviceServers)


def get_instance_name():
    # Tango device servers are always launched with the instance name as the
    # first argument, so try to return it.
    if len(sys.argv) > 0:
        return sys.argv[1]
    else:
        return 'mid_dish_unset'


if __name__ == "__main__":
    main()