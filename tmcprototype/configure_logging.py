from tango import DeviceProxy
import json

# Connected to the databaseds

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
with open('/app/tmcprototype/devices.json', 'r') as file:
    jsonDevices = file.read().replace('\n', '')


# Creating SKALogger DeviceProxy
logger_proxy = DeviceProxy("ref/elt/logger")

# Loading devices.json file and creating an object
json_devices = json.loads(jsonDevices)

for device in json_devices:
    # Setting Logging Level and Logging Target
    device_proxy = DeviceProxy(device["devName"])
    device_proxy.set_logging_level(5)
    device_proxy.add_logging_target("device::ref/elt/logger")

    # Setting Element Logging Level
    logger_proxy.command_inout("SetElementLoggingLevel", ([5], [device["devName"]]))
