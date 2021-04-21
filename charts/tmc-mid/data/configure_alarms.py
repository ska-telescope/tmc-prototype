#!/usr/bin/env python
from tango import DeviceProxy
import json

# print("CREATING CentralNode deviceproxy")
# cn_proxy = DeviceProxy("ska_mid/tm_central/central_node")
# attr_config = cn_proxy.get_attribute_config("telescopeHealthState")
# print("attr_config ----------------", str(attr_config))
# data = cn_proxy.read_attribute("telescopeHealthState")
# print("Attribute telescopehealthstate ----------------: ", str(data))
# print("Attribute telescopehealthstate quality ----------: ", str(data.quality))

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/ska-tmc/devices.json
with open("data/alarms.json", "r") as file:
    jsonAlarmsString = file.read().replace("\n", "")

# Creating DeviceProxy for Alarm Handler device
alarmHandler_proxy = DeviceProxy("ska_mid/tm_alarmhandler/tmalarmhandler")

# Configure Alarms on DishMaster WindSpeed attribute
# Loading alarms.json file and creating an object
try:
    json_alarms = json.loads(jsonAlarmsString)
    print("json_alarms: ", str(json_alarms))
except Exception as e:
    print("Exception in JSON parsing:", e.__str__())

for alarm in json_alarms:
    alarmHandler_proxy.command_inout("Load", alarm["input_string"])
