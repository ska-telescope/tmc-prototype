#!/usr/bin/env python
# Standard python import
import sys
import os
# Additional import
from .utils import get_tango_server_class
import tango
from tango.server import run

# File generated on Mon Jul 12 13:24:36 2021 by tango-simlib-generator


def get_csp_master_simulator():
    device_name = "mid_csp/elt/master"
    tango_ds = get_tango_server_class(device_name)
    return tango_ds[0]

def main(args=None, **kwargs):    
    """
    Runs the CspMasterSimulator.

    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO

    :return: CspMasterSimulator TANGO object.

    """
    CspMasterSimulator = get_csp_master_simulator()
    ret_val = run((CspMasterSimulator,), args=args, **kwargs)
    return ret_val

if __name__ == "__main__":
    main()