#!/usr/bin/env python
from tango import Database, DbDevInfo
from time import sleep
import json

timeSleep = 30
for x in range(10):
    try:
        print("Connecting to the databaseds...")
        db = Database()
    except:
        print("Could not connect to the databaseds. Retry after " + str(timeSleep) + " seconds.")
        sleep(timeSleep)

print("Connected to the databaseds")
with open('/app/tmcprototype/devices.json', 'r') as file:
    jsonDevices = file.read().replace('\n', '')

print(jsonDevices)
json_devices = json.loads(jsonDevices)
for device in json_devices:
    dev_info = DbDevInfo()
    dev_info._class = device["class"]
    dev_info.server = device["serverName"]
    dev_info.name = device["name"]
    print("Adding device:  " + dev_info.name)
    db.add_device(dev_info)
    print("Device: " + dev_info.name + " added.")
    for property in device["properties"]:
        print("Adding property: " + property["name"])
        db.put_device_property(dev_info.name, {property["name"]: property["value"]})
        print("Added property: " + property["name"] + " with value: " + property["value"])
