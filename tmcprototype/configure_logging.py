from tango import DeviceProxy, DevFailed
import json
import time

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
config_json_file = '/app/tmcprototype/devices.json'

with open(config_json_file, 'r') as file:
    jsonDevices = file.read().replace('\n', '')

# Creating SKALogger DeviceProxy
logger_device = "ref/elt/logger"
logger_proxy = DeviceProxy(logger_device)

logging_target = "device::" + logger_device

# Parse json
json_devices = json.loads(jsonDevices)

for device in json_devices:
    if device["devName"] != logger_device:
        # Set Logging Level property
        device_proxy = DeviceProxy(device["devName"])
        device_proxy.set_logging_level(5)
        time.sleep(3)

        try:
            # Set Logging target
            device_proxy.add_logging_target(logging_target)
            time.sleep(3)
        except DevFailed as df:
            print("Failed to set logging target: ", df)

         # Setting Element Logging Level attribute on the deivce
        logger_proxy.command_inout("SetCentralLoggingLevel", ([5], [device["devName"]]))
        time.sleep(3)
        logger_proxy.command_inout("SetElementLoggingLevel", ([5], [device["devName"]]))
        time.sleep(3)
