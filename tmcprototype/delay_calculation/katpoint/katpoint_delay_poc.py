import katpoint
from katpoint import  conversion, ephem_extra
import numpy


# convert ecef coordinates to lat, long, alt of reference antenna
def ecef_to_lla_dms(x,y,z):
    lla = conversion.ecef_to_lla(x,y,z)
    lat_dms = ephem_extra.rad2deg(lla[0])
    long_dms = ephem_extra.rad2deg(lla[1])
    alt = lla[2]
    return lat_dms, long_dms, alt

# Create timestamp oblect
timestamp = katpoint.Timestamp('2019-08-06 11:00:00.000')
print(timestamp.to_mjd())

# # Create target object
target = katpoint.Target('radec , 19:39:25.03 , -63:42:45.7')
print("target: ", target)

# Reference Antenna Object
refx = 1000.0
refy = 1299.0
refz = 6380000.0
#
ref_lat, ref_long, ref_alt = ecef_to_lla_dms(refx, refy, refz)
#
ref_antenna = katpoint.Antenna('ref_ant', str(ref_lat), str(ref_long), str(ref_alt), '0.0', '0.0 0.0 0.0 0.0 0.0 0.0')
print(ref_antenna)

# Create Antenna 1 Object
# Antenna 1 ecef coorinates in meters
ant1_x = 1500.0
ant1_y = 1500.0
ant1_z = 6380000.0
# Convert ecef to enu coordinates
ant1_e, ant1_n, ant1_u = conversion.ecef_to_enu(ref_lat, ref_long, ref_alt, ant1_x, ant1_y, ant1_z)
ant1_delay_model = katpoint.DelayModel([ant1_e, ant1_n, ant1_u,0,0,0])
antenna1 = katpoint.Antenna('A1', str(ref_lat), str(ref_long), str(ref_alt), '0.0', ant1_delay_model)
print(antenna1)

# Create DelayCorrection Object
delay_correction = katpoint.DelayCorrection([antenna1], ref_antenna)

# Calculate geometric delay value
delay_array = delay_correction._calculate_delays(target, timestamp)
print("calculate delay:", delay_array)

# Calculate delay and phase correction values
delays_corrections, phases_corrections = delay_correction.corrections(target, timestamp)
print("delays_corrections: ", delays_corrections)
print("phases_corrections: ", phases_corrections)


# Calculate actual delay values: delay_value + delay_correction_value
actual_delay_h = delay_array[0] + delays_corrections['A1h']
print(delays_corrections['A1h'])
print("actual_delay_h: ", actual_delay_h)



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
