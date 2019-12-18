import katpoint
from katpoint import  conversion, ephem_extra

# convert ecef coordinates to lat, long, alt of reference antenna
def ecef_to_lla_dd_rad(x,y,z):
    lla = conversion.ecef_to_lla(x,y,z)
    lat_rad = lla[0]
    long_rad = lla[1]
    print("lla is: ", lla)
    lat_dd = ephem_extra.rad2deg(lla[0])
    long_dd = ephem_extra.rad2deg(lla[1])
    alt = lla[2]
    return lat_dd, long_dd, alt, lat_rad, long_rad

# # Create target object
target = katpoint.Target('radec , 2:31:50.91 , 89:15:51.4')
print("target: ", target)

# Reference Antenna Object
refx = 1000.0
refy = 1299.0
refz = 6380000.0
#
ref_lat_dd, ref_long_dd, ref_alt, ref_lat_rad, ref_long_rad = ecef_to_lla_dd_rad(refx, refy, refz)
#
ref_antenna_delay_model = katpoint.DelayModel([0.0,0.0,0.0,0.0,0.0,0.0])
ref_antenna = katpoint.Antenna('ref_ant', ref_lat_rad, ref_long_rad, ref_alt, '0.0', ref_antenna_delay_model,[0],0)
print(ref_antenna)
# Create Antenna 1 Object
# Antenna 1 ecef coorinates in meters
ant1_x = 1500.0
ant1_y = 1500.0
ant1_z = 6380000.0
# Convert ecef to enu coordinates
ant1_e, ant1_n, ant1_u = conversion.ecef_to_enu(ref_lat_rad, ref_long_rad, ref_alt, ant1_x, ant1_y, ant1_z)
ant1_delay_model = katpoint.DelayModel([ant1_e, ant1_n, ant1_u,0,0,0])
antenna1 = katpoint.Antenna('A1', ref_lat_rad, ref_long_rad, ref_alt, '0.0', ant1_delay_model,[0],0)
print(antenna1)

# Create DelayCorrection Object
delay_correction = katpoint.DelayCorrection([antenna1], ref_antenna)

delay_h_array = []
delay_v_array = []
delay_corrections_h_array = []
delay_corrections_v_array = []
actual_delay_h_array = []

# timestamps array
timestamp_array = ['2019-08-06 11:0.0:00.000', '2019-08-06 11:1.0:00.000', '2019-08-06 11:2.0:00.000', '2019-08-06 11:3.0:00.000', '2019-08-06 11:4.0:00.000', '2019-08-06 11:5.0:00.000', '2019-08-06 11:6.0:00.000', '2019-08-06 11:7.0:00.000', '2019-08-06 11:8.0:00.000', '2019-08-06 11:9.0:00.000', '2019-08-06 11:10.0:00.000', '2019-08-06 11:11.0:00.000', '2019-08-06 11:12.0:00.000', '2019-08-06 11:13.0:00.000', '2019-08-06 11:14.0:00.000', '2019-08-06 11:15.0:00.000', '2019-08-06 11:16.0:00.000', '2019-08-06 11:17.0:00.000', '2019-08-06 11:18.0:00.000', '2019-08-06 11:19.0:00.000', '2019-08-06 11:20.0:00.000', '2019-08-06 11:21.0:00.000', '2019-08-06 11:22.0:00.000', '2019-08-06 11:23.0:00.000', '2019-08-06 11:24.0:00.000', '2019-08-06 11:25.0:00.000', '2019-08-06 11:26.0:00.000', '2019-08-06 11:27.0:00.000', '2019-08-06 11:28.0:00.000', '2019-08-06 11:29.0:00.000', '2019-08-06 11:30.0:00.000', '2019-08-06 11:31.0:00.000', '2019-08-06 11:32.0:00.000', '2019-08-06 11:33.0:00.000', '2019-08-06 11:34.0:00.000', '2019-08-06 11:35.0:00.000', '2019-08-06 11:36.0:00.000', '2019-08-06 11:37.0:00.000', '2019-08-06 11:38.0:00.000', '2019-08-06 11:39.0:00.000', '2019-08-06 11:40.0:00.000', '2019-08-06 11:41.0:00.000', '2019-08-06 11:42.0:00.000', '2019-08-06 11:43.0:00.000', '2019-08-06 11:44.0:00.000', '2019-08-06 11:45.0:00.000', '2019-08-06 11:46.0:00.000', '2019-08-06 11:47.0:00.000', '2019-08-06 11:48.0:00.000', '2019-08-06 11:49.0:00.000', '2019-08-06 11:50.0:00.000', '2019-08-06 11:51.0:00.000', '2019-08-06 11:52.0:00.000', '2019-08-06 11:53.0:00.000', '2019-08-06 11:54.0:00.000', '2019-08-06 11:55.0:00.000', '2019-08-06 11:56.0:00.000', '2019-08-06 11:57.0:00.000', '2019-08-06 11:58.0:00.000', '2019-08-06 11:59.0:00.000']
for i in range(0,len(timestamp_array)):
    # create timestamp object
    timestamp = katpoint.Timestamp(timestamp_array[i])
    # Calculate geometric delay value
    delay = delay_correction._calculate_delays(target, timestamp)
    delay_h_array.append(delay[0])
    delay_v_array.append(delay[1])
    # Calculate delay and phase correction values
    delays_corrections, phases_corrections = delay_correction.corrections(target, timestamp)
    delay_corrections_h_array.append(delays_corrections['A1h'])
    delay_corrections_v_array.append(delays_corrections['A1v'])

    # Calculate actual delay values: delay_value + delay_correction_value
    actual_delay_h = delay[0] + delays_corrections['A1h']
    actual_delay_h_array.append(actual_delay_h)
    print(delays_corrections['A1h'])

print("------------------------------------------------------------------------------------------")
print("calculate delay h: ", delay_h_array)
print("------------------------------------------------------------------------------------------")
print("calculate delay v: ", delay_v_array)
print("------------------------------------------------------------------------------------------")
print("delay_corrections_h_array: ", delay_corrections_h_array)
print("------------------------------------------------------------------------------------------")
print("delay_corrections_v_array: ", delay_corrections_v_array)
print("------------------------------------------------------------------------------------------")
print("actual_delay_h_array: ", actual_delay_h_array)
print("------------------------------------------------------------------------------------------")
# # Load a set of antenna descriptions and construct Antenna objects from them
# with open('ska_antennas.txt') as f:
#     descriptions = f.readlines()
# antennas = [katpoint.Antenna(line) for line in descriptions]
# antennas = {ant.name: ant for ant in antennas}
#
# #  Construct a Target object
# target = katpoint.Target('radec , 19:39:25.03 , -63:42:45.7')
#
# # Timestamp in date string
# timestamp = katpoint.Timestamp('2019-04-29 21:51:00.9701018')
#
# with open('ska_delay_model.txt') as f:
#     array_model_json = f.readline()
# array_model = katpoint.DelayCorrection(array_model_json)
#
# # two delay values per antenna
# array_delays = array_model._calculate_delays(target, timestamp)
# print("array_delays: ", array_delays)
#
# # Delay and Phase corrections
# delays_corrections, phases_corrections = array_model.corrections(target, timestamp)
# print("delays_corrections: ", delays_corrections)
# print("phases_corrections: ", phases_corrections)
#
# # Apply delays_corrections on array_delays to obtain correct delay values