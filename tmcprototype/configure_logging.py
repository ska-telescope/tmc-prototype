import sys
import json
import time
from tango import DeviceProxy, DevFailed

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
config_json_file = '/app/tmcprototype/devices.json'
with open(config_json_file, 'r') as file:
    str_json_devices = file.read().replace('\n', '')

# Creating SKALogger DeviceProxy
logger_device = "ref/elt/logger"
logger_proxy = DeviceProxy(logger_device)

max_retries = 10
retry = 0
while retry < max_retries:
    try:
        logger_proxy.ping()
        break
    except DevFailed:
        time.sleep(3)
        retry += 1

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
                    device_server != "Databaseds" and
                    device_server != "TangoAccessControl"
                ):
                    server_instance_list = device_servers[device_server].keys()
                    for server_instance in server_instance_list:
                        devices_class_list = device_servers[device_server][server_instance].keys()
                        for devices_class in devices_class_list:
                            device_name_list = device_servers[device_server][server_instance][devices_class].keys()
                            for device_name in device_name_list:
                                device_proxy = DeviceProxy(device_name)
                                # Set Logging Level property
                                device_proxy.add_logging_target(logging_target)
                                # Set logging levels of the device
                                logger_proxy.command_inout("SetCentralLoggingLevel", ([5], device_name))
                                logger_proxy.command_inout("SetElementLoggingLevel", ([5], device_name))
                                logger_proxy.command_inout("SetStorageLoggingLevel", ([5], device_name))
            except DevFailed as df:
                print("Exception:", df)
    except Exception as ex:
        print("Exception: ", ex)
    ret_val = 0
else:
    print("Logger device not ready")
    ret_val = -1

sys.exit(ret_val)