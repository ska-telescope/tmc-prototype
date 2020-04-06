#!/usr/bin/env python
from tango import DeviceProxy
import json

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
with open('/app/tmcprototype/tmalarmhandler/alarms.json', 'r') as file:
    jsonAlarmsString = file.read().replace('\n', '')

# Creating DeviceProxy for Alarm Handler device
alarmHandler_proxy = DeviceProxy("ska_mid/tm_alarmhandler/tmalarmhandler")

# Configure Alarms on DishMaster WindSpeed attribute
# Loading alarms.json file and creating an object
try:
    json_alarms = json.loads(jsonAlarmsString)
except Exception as e:
    print("Exception in JSON parsing:", e.__str__())

for alarm in json_alarms:
    alarmHandler_proxy.command_inout("Load", alarm["input_string"])