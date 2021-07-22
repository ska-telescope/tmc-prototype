import pkg_resources
import logging

from tango_simlib.tango_sim_generator import (configure_device_models, get_tango_device_server)

# from ska.logging import configure_logging


def get_tango_server_class(device_name):
    """Build and return the Tango device class for CspSubarray

    :param device_name: str
        The Tango device name
    :return CspSubarray: tango.server.Device
        The Tango device class for CspSubarray
    """
    # data_descr_files = []
    # data_descr_files.append(
    #     pkg_resources.resource_filename("dishmaster", "dish_master.fgo")
    # )
    # data_descr_files.append(
    #     pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json")
    # )

    # add a filter with this device's name
    device_name_tag = f"tango-device:{device_name}"

    class TangoDeviceTagsFilter(logging.Filter):
        def filter(self, record):
            record.tags = device_name_tag
            return True

    # set up Python logging
    # configure_logging(tags_filter=TangoDeviceTagsFilter)
    logger_name = f"csp-subarray-{device_name}"
    logger = logging.getLogger(logger_name)
    logger.info("Logging started for %s.", device_name)
    configure_args = {"logger": logger}
    # test/nodb/cspsubarray is used for testing
    if device_name == "test/nodb/cspsubarray":
        configure_args["test_device_name"] = device_name
    
    sim_data_files = ['/home/ubuntu/projects/ska-tmc/ska-tmc/cspsubarrayleafnode/src/cspsubarrayleafnode/cspsubarraysimulator/CspSubarray.fgo','/home/ubuntu/projects/ska-tmc/ska-tmc/cspsubarrayleafnode/src/cspsubarrayleafnode/cspsubarraysimulator/csp_subarray_SimDD.json']
    models = configure_device_models(sim_data_files)
    TangoDeviceServers = get_tango_device_server(models, sim_data_files)
    # server_run(TangoDeviceServers)

    # model = configure_device_model(data_descr_files, **configure_args)
    # DishMaster, _ = get_tango_device_server(model, data_descr_files)
    return TangoDeviceServers
