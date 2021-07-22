#!/usr/bin/env python
from tango.server import server_run
from tango_simlib.tango_sim_generator import (configure_device_models, get_tango_device_server)


# File generated on Tue Jul 13 14:32:08 2021 by tango-simlib-generator

class CspMasterSimulator():
    def simulator():
        sim_data_files = ['/home/ubuntu/projects/ska-tmc/ska-tmc/cspmasterleafnode/src/cspmasterleafnode/cspmastersimulator/CspMaster.fgo','/home/ubuntu/projects/ska-tmc/ska-tmc/cspmasterleafnode/src/cspmasterleafnode/cspmastersimulator/csp_master_simDD.json']
        models = configure_device_models(sim_data_files)
        TangoDeviceServers = get_tango_device_server(models, sim_data_files)
        return(TangoDeviceServers)

# if __name__ == "__main__":
#     main()
