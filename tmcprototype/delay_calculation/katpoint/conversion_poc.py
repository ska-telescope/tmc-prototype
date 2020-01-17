

import katpoint
from katpoint import  conversion, ephem_extra
import matplotlib.pyplot as plt


# Load a set of antenna descriptions and construct Antenna objects from them
with open('ska_antennas.txt') as f:
    descriptions = f.readlines()
antennas = [katpoint.Antenna(line) for line in descriptions]
antennas = {ant.name: ant for ant in antennas}

ref_ant = antennas['m000']
print(ref_ant)
antenna1 = antennas['m059']
print(antenna1)

# Create DelayCorrection Object
delay_correction = katpoint.DelayCorrection([antenna1], ref_ant)
print("delay_correction: ", delay_correction)


# Create target object
target = katpoint.Target('radec , 21:08:47.89 , -88:57:23.0')
delay_h_array = []
delay_v_array = []
delay_corrections_h_array = []
delay_corrections_v_array = []
actual_delay_h_array = []

# timestamps array starting from 00:00:00.000 to 23:59:00.000 at an interval of 1 min on 2019-08-06
timestamp_array = ['2019-08-06 0:0:00', '2019-08-06 0:0:01', '2019-08-06 0:0:02', '2019-08-06 0:0:03', '2019-08-06 0:0:04', '2019-08-06 0:0:05', '2019-08-06 0:0:06', '2019-08-06 0:0:07', '2019-08-06 0:0:08', '2019-08-06 0:0:09', '2019-08-06 0:0:10', '2019-08-06 0:0:11', '2019-08-06 0:0:12', '2019-08-06 0:0:13', '2019-08-06 0:0:14', '2019-08-06 0:0:15', '2019-08-06 0:0:16', '2019-08-06 0:0:17', '2019-08-06 0:0:18', '2019-08-06 0:0:19', '2019-08-06 0:0:20', '2019-08-06 0:0:21.000', '2019-08-06 0:0:22.000', '2019-08-06 0:0:23.000', '2019-08-06 0:0:24.000', '2019-08-06 0:0:25.000', '2019-08-06 0:0:26.000', '2019-08-06 0:0:27.000', '2019-08-06 0:0:28.000', '2019-08-06 0:0:29.000', '2019-08-06 0:0:30.000', '2019-08-06 0:0:31.000', '2019-08-06 0:0:32.000', '2019-08-06 0:0:33.000', '2019-08-06 0:0:34.000', '2019-08-06 0:0:35.000', '2019-08-06 0:0:36.000', '2019-08-06 0:0:37.000', '2019-08-06 0:0:38.000', '2019-08-06 0:0:39.000', '2019-08-06 0:0:40.000', '2019-08-06 0:0:41.000', '2019-08-06 0:0:42.000', '2019-08-06 0:0:43.000', '2019-08-06 0:0:44.000', '2019-08-06 0:0:45.000', '2019-08-06 0:0:46.000', '2019-08-06 0:0:47.000', '2019-08-06 0:0:48.000', '2019-08-06 0:0:49.000', '2019-08-06 0:0:50.000', '2019-08-06 0:0:51.000', '2019-08-06 0:0:52.000', '2019-08-06 0:0:53.000', '2019-08-06 0:0:54.000', '2019-08-06 0:0:55.000', '2019-08-06 0:0:56.000', '2019-08-06 0:0:57.000', '2019-08-06 0:0:58.000', '2019-08-06 0:0:59.000','2019-08-06 0:01:0.000']
for i in range(0,len(timestamp_array)):
    # create timestamp object
    timestamp = katpoint.Timestamp(timestamp_array[i])
    # Calculate geometric delay value
    delay = delay_correction._calculate_delays(target, timestamp)
    delay_h_array.append(delay[0])
    delay_v_array.append(delay[1])
    # print(delay[0])

print("------------------------------------------------------------------------------------------")
print("calculate delay h: ", delay_h_array)
print("------------------------------------------------------------------------------------------")
#print("calculate delay v: ", delay_v_array)

print("------------------------------------------------------------------------------------------")

index = list(range(60))
plt.plot(index , delay_h_array)
plt.show()