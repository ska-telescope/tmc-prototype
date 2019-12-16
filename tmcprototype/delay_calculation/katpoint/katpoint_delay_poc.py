import katpoint

# Load a set of antenna descriptions and construct Antenna objects from them
with open('ska_antennas.txt') as f:
    descriptions = f.readlines()
antennas = [katpoint.Antenna(line) for line in descriptions]
antennas = {ant.name: ant for ant in antennas}

#  Construct a Target object
target = katpoint.Target('radec , 19:39:25.03 , -63:42:45.7')

# Timestamp in date string
timestamp = katpoint.Timestamp('2019-04-29 21:51:00.9701018')

with open('ska_delay_model.txt') as f:
    array_model_json = f.readline()
array_model = katpoint.DelayCorrection(array_model_json)

# two delay values per antenna
array_delays = array_model._calculate_delays(target, timestamp)
print("array_delays: ", array_delays)

# Delay and Phase corrections
delays_corrections, phases_corrections = array_model.corrections(target, timestamp)
print("delays_corrections: ", delays_corrections)
print("phases_corrections: ", phases_corrections)

# Apply delays_corrections on array_delays to obtain correct delay values





































# # Get current time in UTC format and convert it to string
# timestamp1 = katpoint.Timestamp('2019-04-29 21:51:00.9701018')
# timestamp_string = timestamp1.to_string()
# print("timestamp: ", timestamp1)
#
# # Create target object
# target1 = katpoint.Target('radec , 19:39:25.03 , -63:42:45.7')
# print("target 1 ", target1)
#
# # Antenna(name, latitude=None, longitude=None, altitude=None, diameter=0.0, delay_model=None, pointing_model=None, beamwidth=1.22)
#
# ref_antenna = katpoint.Antenna('A, 18.5304, 73.7667, 0, 12.0, 0.0 0.0 0.0')
# antenna1 = katpoint.Antenna('A1, 18.5304, 73.7667, 0, 12.0, 50.0 -50.0 0.0')
# antenna2 = katpoint.Antenna('A2, 18.5304, 73.7667, 0, 12.0, 5.0 10.0 3.0')
#
# # create delay object
# delay1 = katpoint.DelayCorrection([antenna1, antenna2], ref_antenna)
#
# b = delay1._calculate_delays(target1, timestamp_string)
# print("calculate delay:", b)
#
# c = delay1.corrections(target1, timestamp1)
# print("Corrections:", c)
