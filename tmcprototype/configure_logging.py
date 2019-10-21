import sys
import json
import time
import numpy as np
from tango import DeviceProxy, DevFailed

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
config_json_file = '/app/data/tmc-devices.json'
with open(config_json_file, 'r') as file:
    str_json_devices = file.read().replace('\n', '')

# Creating SKALogger DeviceProxy
logger_device = "ref/elt/logger"
logger_proxy = DeviceProxy(logger_device)
print("Logger_proxy is :",logger_proxy)


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
    print(" loggging target is",logging_target)

    try:
        # Parse json
        json_devices = json.loads(str_json_devices)
        device_servers = json_devices["servers"]

        for device_server in device_servers:
            try:

                if (device_server != "SKALogger" and
                    device_server != "TangoTest" and
                    device_server != "DataBase" and
                    device_server != "TangoAccessControl"
                ):
                    server_instance_list = device_servers[device_server].keys()
                    #print("server_instance_list is", server_instance_list)
                    for server_instance in server_instance_list:
                        devices_class_list = device_servers[device_server][server_instance].keys()
                        for devices_class in devices_class_list:
                            device_name_list = device_servers[device_server][server_instance][devices_class].keys()
                            for device_name in device_name_list:
                                print("device name is", device_name)
                                device_proxy = DeviceProxy(device_name)
                                print("device_proxy name is",device_proxy)

                                # Set Logging Level property
                                print ("Logging target:", logging_target)
                                device_proxy.add_logging_target(logging_target)
                                try:
                                    logging_level = []
                                    logging_level.append(5)
                                    source_device = []
                                    source_device.append(device_name)
                                    device_details = []
                                    device_details.append(logging_level)
                                    device_details.append(source_device)
                                    logger_proxy.command_inout("SetCentralLoggingLevel",device_details)
                                    logger_proxy.command_inout("SetElementLoggingLevel",device_details)
                                    logger_proxy.command_inout("SetStorageLoggingLevel",device_details)
                                except Exception as ex:
                                    print ("Exception occured.",ex)
            except DevFailed as df:
                print("Exception:", df)
    except Exception as ex:
        print("Exception: ", ex)
    ret_val = 0
else:
    print("Logger device not ready")
    ret_val = -1

sys.exit(ret_val)