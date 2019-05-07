#!/usr/bin/env python
from tango import AttributeProxy, ChangeEventInfo, AttributeInfoEx
import json

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json

# with open('/home/user/projects/tmc-prototype/tmcprototype/devices.json', 'r') as file:
#     jsonDevices = file.read().replace('\n', '')

with open('/app/tmcprototype/devices.json', 'r') as file:
    jsonDevices = file.read().replace('\n', '')

# Loading devices.json file and creating an object
json_devices = json.loads(jsonDevices)

for device in json_devices:
    deviceName = device["devName"]

    for attributeProperty in device["attributeProperties"]:
        attributeProxy = AttributeProxy(deviceName + "/" + attributeProperty["attributeName"])
        print("Device: ", deviceName, " Attribute: ", attributeProperty["attributeName"])
        print("Polling Period: ", attributeProperty["pollingPeriod"])
        if(attributeProperty["pollingPeriod"] != ""):
            attributeProxy.poll(attributeProperty["pollingPeriod"])
        else:
            print("Skip setting polling period...")
        if(attributeProperty["changeEventAbs"] != ""):
            attrInfoEx = attributeProxy.get_config()
            absChange = ChangeEventInfo()
            absChange.abs_change = attributeProperty["changeEventAbs"]
            attrInfoEx.events.ch_event = absChange
            attributeProxy.set_config(attrInfoEx)
        else:
            print("Skip setting change event absolute...")