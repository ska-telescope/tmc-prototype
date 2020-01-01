import katpoint
from scipy.interpolate import UnivariateSpline
import numpy as np
import matplotlib.pyplot as plt

# Load a set of antenna descriptions and construct Antenna objects from them
with open('ska_antennas.txt') as f:
    descriptions = f.readlines()
antennas = [katpoint.Antenna(line) for line in descriptions]
print("\n", "antennas 1: ", antennas, type(antennas))
antennas_dict = {ant.name: ant for ant in antennas}

ref_ant = antennas_dict['m000']
#print(ref_ant)

# Create DelayCorrection Object
delay_correction = katpoint.DelayCorrection(antennas, ref_ant)
#print("delay_correction: ", delay_correction)

# Create target object
target = katpoint.Target('radec , 20:21:10.31 , -30:52:17.3')
delay_corrections_h_array_t0 = []
delay_corrections_h_array_t1 = []
delay_corrections_h_array_t2 = []
delay_corrections_h_array_t3 = []
delay_corrections_h_array_t4 = []
delay_corrections_h_array_t5 = []
delay_corrections_h_array_dict = {}
delay_corrections_v_array_t0 = []
delay_corrections_v_array_t1 = []
delay_corrections_v_array_t2 = []
delay_corrections_v_array_t3 = []
delay_corrections_v_array_t4 = []
delay_corrections_v_array_t5 = []
delay_corrections_v_array_dict = {}

# timestamps array starting from 00:00:00.000 to 23:59:00.000 at an interval of 1 min on 2019-08-06
timestamp_array = ['2019-08-06 0:0:00.000', '2019-08-06 0:0:02.000', '2019-08-06 0:0:04.000', '2019-08-06 0:0:06.000', '2019-08-06 0:0:08.000', '2019-08-06 0:0:10.000']
for timestamp in range(0, len(timestamp_array)):
    # Calculate geometric delay value
    delay = delay_correction._calculate_delays(target, timestamp_array[timestamp])
    antenna_names = list(delay_correction.ant_models.keys())

    # Horizontal and vertical delay corrections for each antenna
    for i in range(0,len(delay)):
        if i%2 == 0:
            if timestamp ==0:
                delay_corrections_h_array_t0.append(delay[i])
            elif timestamp ==1:
                delay_corrections_h_array_t1.append(delay[i])
            elif timestamp ==2:
                delay_corrections_h_array_t2.append(delay[i])
            elif timestamp ==3:
                delay_corrections_h_array_t3.append(delay[i])
            elif timestamp ==4:
                delay_corrections_h_array_t4.append(delay[i])
            elif timestamp ==5:
                delay_corrections_h_array_t5.append(delay[i])

        else:
            if timestamp ==0:
                delay_corrections_v_array_t0.append(delay[i])
            elif timestamp ==1:
                delay_corrections_v_array_t1.append(delay[i])
            elif timestamp ==2:
                delay_corrections_v_array_t2.append(delay[i])
            elif timestamp ==3:
                delay_corrections_v_array_t3.append(delay[i])
            elif timestamp ==4:
                delay_corrections_v_array_t4.append(delay[i])
            elif timestamp ==5:
                delay_corrections_v_array_t5.append(delay[i])


x = np.array([0, 0.2, 0.4, 0.6, 0.8, 1])
for i in range(0, len(antenna_names)):
    temp_delay_list = []
    temp_delay_list.append(delay_corrections_h_array_t0[i])
    temp_delay_list.append(delay_corrections_h_array_t1[i])
    temp_delay_list.append(delay_corrections_h_array_t2[i])
    temp_delay_list.append(delay_corrections_h_array_t3[i])
    temp_delay_list.append(delay_corrections_h_array_t4[i])
    temp_delay_list.append(delay_corrections_h_array_t5[i])

    # x should be independent and y should be independent
    # The number of data points must be larger than the spline degree `k`
    y = np.array(temp_delay_list)

    output = UnivariateSpline(x, y, k=5, s=0)
    poly= output.get_coeffs()
    delay_corrections_h_array_dict[antenna_names[i]] = poly

    #xs = np.linspace(0, 1, )
    plt.plot(x, output(x), 'g', lw=3)



print("antenna_names: ", antenna_names)
print("delay_corrections_h_array_t0: ", delay_corrections_h_array_t0)
print("delay_corrections_h_array_dict: ", delay_corrections_h_array_dict)
# print("delay_corrections_v_array_dict: ", delay_corrections_v_array_dict)

#
# xs = np.linspace(0, 1)
# plt.plot(xs, output1(xs), 'g', lw=3)
plt.show()
