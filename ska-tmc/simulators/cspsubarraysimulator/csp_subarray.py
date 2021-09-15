#!/usr/bin/env python
# Standard python import
import sys
import os
# Additional import
from .utils import get_tango_server_class
import tango
from tango.server import run

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

def main(args=None, **kwargs):    
    """
    Runs the CspSubarrayLeafNodeSimulator.

    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO

    :return: CspSubarrayLeafNodeSimulator TANGO object.

    """
    # try:
    #     standalone_mode = os.environ["STANDALONE_MODE"]
    # except KeyError:
    #     standalone_mode = "false"

    # if standalone_mode == "true":
    CspSubarrayLeafNodeSimulator = csp_subarray_simulator()
    # csp_subarray_simulator_list.append(csp_subarray_server())
    # csp_subarray_simulator_list.append(CspSubarrayLeafNode)
    ret_val = run((CspSubarrayLeafNodeSimulator,), args=args, **kwargs)

    return ret_val

if __name__ == "__main__":
    main()