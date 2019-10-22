import sys
import json
import time
import tango
from tango import DeviceProxy, DevFailed

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
config_json_file = '/app/data/tmc-devices.json'
with open(config_json_file, 'r') as file:
    str_json_devices = file.read().replace('\n', '')

# Creating SKALogger DeviceProxy
logger_device = "ref/elt/logger"
logger_proxy = DeviceProxy(logger_device)
# Check if Logger device is up and running
max_retries = 10
retry = 0
while retry < max_retries:
    try:

        break
    except DevFailed:
        time.sleep(3)
        retry += 1

excpt_msg = []
excpt_count = 0
if(retry < max_retries):
    logging_target = "device::" + logger_device

    try:
        # Parse json
        json_devices = json.loads(str_json_devices)
        device_servers = json_devices["servers"]

        for device_server in device_servers:
            try:
                if (device_server != "SKALogger" and
                    device_server != "TangoTest" and
                    device_server != "DataBaseds" and
                    device_server != "TangoAccessControl"
                ):
                    server_instance_list = device_servers[device_server].keys()
                    for server_instance in server_instance_list:
                        devices_class_list = device_servers[device_server][server_instance].keys()
                        for devices_class in devices_class_list:
                            device_name_list = \
                                device_servers[device_server][server_instance][devices_class].keys()
                            for device_name in device_name_list:
                                device_proxy = DeviceProxy(device_name)
                                # Set Logging Level property
                                device_proxy.add_logging_target(logging_target)
                                try:
                                    # Set logging level value
                                    logging_level = []
                                    logging_level.append(5)
                                    # Add source TANGO device for logging
                                    source_device = []
                                    source_device.append(device_name)
                                    device_details = []
                                    device_details.append(logging_level)
                                    device_details.append(source_device)
                                    # Invoke Set commands at logger device to update logging levels
                                    logger_proxy.command_inout("SetCentralLoggingLevel",device_details)
                                    logger_proxy.command_inout("SetElementLoggingLevel",device_details)
                                    logger_proxy.command_inout("SetStorageLoggingLevel",device_details)
                                except Exception as except_occurred:
                                    print ("Exception :", except_occurred)
                                    excpt_msg.append(except_occurred)
                                    excpt_count += 1
            except DevFailed as dev_failed:
                print("Exception: ", dev_failed)
                excpt_msg.append(dev_failed)
                excpt_count += 1
    except Exception as except_occurred:
        print("Exception : ", except_occurred)
        excpt_msg.append(except_occurred)
        excpt_count += 1
    ret_val = 0
else:
    print("Logger device is not ready.")
    ret_val = -1

if excpt_count > 0:
    err_msg = ' '
    for item in excpt_msg:
        err_msg += item + "\n"
    tango.Except.throw_exception(err_msg, tango.ErrSeverity.ERR)

sys.exit(ret_val)