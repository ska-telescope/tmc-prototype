from tango import DeviceProxy
import json

with open('/app/tmcprototype/TMAlarmHandler/alarms.json', 'r') as file:
#with open('/home/user/projects/tmc-prototype/tmcprototype/TMAlarmHandler/alarms.json', 'r') as file:
    jsonAlarmsString = file.read().replace('\n', '')

# Creating DeviceProxy for Alarm Handler device
alarmHandler_proxy = DeviceProxy("alarmhandler/1/1")

# Configure Alarms on DishMaster WindSpeed attribute
# Loading alarms.json file and creating an object
try:
    json_alarms = json.loads(jsonAlarmsString)
except Exception as e:
    print("Exception in JSON parsing:", e.__str__())

for alarm in json_alarms:
    alarmHandler_proxy.command_inout("Load", alarm["input_string"])