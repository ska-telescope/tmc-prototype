import sys
import json
import time
from tango import DeviceProxy, DevFailed

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
config_json_file = '/app/tmcprototype/devices.json'

with open(config_json_file, 'r') as file:
    jsonDevices = file.read().replace('\n', '')

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

    # Parse json
    json_devices = json.loads(jsonDevices)

    for device in json_devices:
        try:
            if device["devName"] != logger_device:
                # Set Logging Level property
                device_proxy = DeviceProxy(device["devName"])
                device_proxy.set_logging_level(5)
                time.sleep(3)

                # Set Logging target
                device_proxy.add_logging_target(logging_target)
                time.sleep(3)

                # Set logging levels of the device
                logger_proxy.command_inout("SetCentralLoggingLevel", ([5], [device["devName"]]))
                time.sleep(3)
                logger_proxy.command_inout("SetElementLoggingLevel", ([5], [device["devName"]]))
                time.sleep(3)
                logger_proxy.command_inout("SetStorageLoggingLevel", ([5], [device["devName"]]))
                time.sleep(3)
        except DevFailed:
            print("Failed to Connect to the device: ", device["devName"])
        except Exception as ex:
            print("Exception occurred while configuring device {}:{}".format(device["devName"], ex))
    ret_val = 0
else:
    print("Logger device not ready")
    ret_val = -1

sys.exit(ret_val)