#!/usr/bin/env python
from tango import Database, DbDevInfo
from time import sleep
import json

timeSleep = 30
for x in range(10):
    try:
        # Connecting to the databaseds
        db = Database()
    except:
        # Could not connect to the databaseds. Retry after: str(timeSleep) seconds.
        sleep(timeSleep)

# Connected to the databaseds

# Update file path to devices.json in order to test locally
# To test on docker environment use path : /app/tmcprototoype/devices.json
with open('/app/tmcprototype/devices.json', 'r') as file:
    jsonDevices = file.read().replace('\n', '')

# Loading devices.json file and creating an object
json_devices = json.loads(jsonDevices)

for device in json_devices:
    dev_info = DbDevInfo()
    dev_info._class = device["class"]
    dev_info.server = device["serverName"]
    dev_info.name = device["devName"]

    # Adding device
    db.add_device(dev_info)

    # Adding device properties
    for deviceProperty in device["deviceProperties"]:
        # Adding device property: deviceProperty["devPropValue"]
        # with value: deviceProperty["devPropValue"]
        db.put_device_property(dev_info.name,
                               {deviceProperty["devPropName"]:
                                    deviceProperty["devPropValue"]})

    # Adding attribute properties
    for attributeProperty in device["attributeProperties"]:
        # Adding attribute property: attributeProperty["attrPropName"]
        # for attribute: attributeProperty["attributeName"]
        # with value: " + attributeProperty["attrPropValue"]
        db.put_device_attribute_property(dev_info.name,
                                         {attributeProperty["attributeName"]:
                                              {attributeProperty["attrPropName"]:
                                                   attributeProperty["attrPropValue"]}})
