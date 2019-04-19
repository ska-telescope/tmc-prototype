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
print("logging_target: ", logging_target)

# Parse json
json_devices = json.loads(jsonDevices)

for device in json_devices:
    print("device name: ", device["devName"])
    if device["devName"] != logger_device:
        # Set Logging Level
        device_proxy = DeviceProxy(device["devName"])
        print("device_proxy : ", device_proxy )
        device_proxy.set_logging_level(5)
        time.sleep(2)

        try:
            # Set Logging target
            device_proxy.add_logging_target(logging_target)
            time.sleep(2)
        except DevFailed as df:
            print("Failed to set logging target: ", df)

         # Setting Element Logging Level
        logger_proxy.command_inout("SetCentralLoggingLevel", ([5], [device["devName"]]))
        time.sleep(2)
        logger_proxy.command_inout("SetElementLoggingLevel", ([5], [device["devName"]]))
        time.sleep(2)
