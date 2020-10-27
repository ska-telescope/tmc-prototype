#!/usr/bin/env python
import logging
import sys

from ska.logging import configure_logging

from tango.server import server_run
from tango_simlib.tango_sim_generator import (configure_device_model, get_tango_device_server)


def main():
    sim_data_files = ['dish_master.fgo',
                      'dish_master_SimDD.json']
    # TODO (SamT 2018-05-18) install these files as part of package instead of abs path

    # set up Python logging
    configure_logging()
    log_name = 'kat.{}'.format(get_instance_name())
    logger = logging.getLogger(log_name)
    logger.info("Logging started for Example application")

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