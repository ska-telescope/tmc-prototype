from scipy.interpolate import UnivariateSpline
import numpy as np

# Calculate 5th order polynomial coefficients

antenna_delay_list = []

x = np.array([0, 2, 4, 6, 8, 10])

# 6 delay values for antenna 1 in the interval 10 seconds
t0_delay = -0.00000050178708094610  # Delay at t0
t1_delay = -0.00000050179250923286  # Delay at t0 + 2
t2_delay = -0.00000050179804711394  # Delay at t0 + 4
t3_delay = -0.00000050180366432404  # Delay at t0 + 6
t4_delay = -0.00000050180939400960  # Delay at t0 + 8
t5_delay = -0.00000050181521815249  # Delay at t0 + 10

antenna_delay_list.append(t0_delay)
antenna_delay_list.append(t1_delay)
antenna_delay_list.append(t2_delay)
antenna_delay_list.append(t3_delay)
antenna_delay_list.append(t4_delay)
antenna_delay_list.append(t5_delay)

y = np.array(antenna_delay_list)

# smoothing factor (s) is 0
# Degree of the smoothing spline (k) is 5 as the coefficients of 5th order are needed.
output = UnivariateSpline(x, y, k=5, s=0)
polynomial_coefficients = output.get_coeffs()
print(polynomial_coefficients)
