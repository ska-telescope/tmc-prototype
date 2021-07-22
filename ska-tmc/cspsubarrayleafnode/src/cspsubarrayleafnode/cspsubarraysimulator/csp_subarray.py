#!/usr/bin/env python
# Standard python import
import sys

# Tango import
#!/usr/bin/env python
from tango.server import server_run

# Additional import
from .utils import get_tango_server_class

# File generated on Mon Jul 12 13:24:36 2021 by tango-simlib-generator

class CspSubarraySimulator():

    def simulator():
        if len(sys.argv) > 0:
            device_name = sys.argv[1]
            if device_name.isdigit():
                device_name = f"mid_csp/elt/subarray_01"
        else:
            device_name = "mid_csp_unset/elt/master"

        TangoDeviceServers = get_tango_server_class(device_name)
        # server_run(TangoDeviceServers)
        return TangoDeviceServers


# if __name__ == "__main__":
#     main()
