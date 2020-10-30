#!/usr/bin/env python
import sys
from tango.server import run
from dishmaster.utils import get_tango_server_class


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
