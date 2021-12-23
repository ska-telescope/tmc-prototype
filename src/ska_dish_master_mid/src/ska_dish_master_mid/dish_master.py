#!/usr/bin/env python
# Standard python import
import sys

# Tango import
from tango.server import run

# Additional import
from src.ska_dish_master_mid.src.ska_dish_master_mid.utils import (
    get_tango_server_class,
)


def main():
    if len(sys.argv) > 0:
        device_name = sys.argv[1]
        if device_name.isdigit():
            device_name = f"mid_d{device_name.zfill(4)}/elt/master"
        else:
            device_name = f"{device_name}/elt/master"
    else:
        device_name = "mid_dish_unset/elt/master"

    DishMaster = get_tango_server_class(device_name)
    run((DishMaster,))


if __name__ == "__main__":
    main()
