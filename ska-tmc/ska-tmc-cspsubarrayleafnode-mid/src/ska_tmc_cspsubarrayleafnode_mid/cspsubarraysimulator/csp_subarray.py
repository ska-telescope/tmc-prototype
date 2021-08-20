#!/usr/bin/env python
# Standard python import
import sys

# Additional import
from .utils import get_tango_server_class

# File generated on Mon Jul 12 13:24:36 2021 by tango-simlib-generator


def csp_subarray_simulator():
    if len(sys.argv) > 0:
        device_name = sys.argv[1]
        if device_name.isdigit():
            device_name = f"mid_csp/elt/subarray_{device_name}"
    else:
        device_name = "mid_csp_unset/elt/master"

    tango_ds = get_tango_server_class(device_name)
    return tango_ds[0]