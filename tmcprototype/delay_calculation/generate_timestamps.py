import katpoint
import numpy

# Create timestamp oblect
timestamp_array =[]
mjd_array = []
for hour in range(0,24):
    for minute in range(0,60):
        time = '2019-08-06 '+ str(hour)+':' + str(minute) + ':00.000'
        # print("time: ", time)
        timestamp_array.append(time)

for i in range(0,len(timestamp_array)):
    timestamp = katpoint.Timestamp(timestamp_array[i])
    mjd_array.append(timestamp.to_mjd())

print("timestamp array: ", timestamp_array)
#print("timestamp array: ", (numpy.array(timestamp_array)).shape)
print("mjd: ", mjd_array)