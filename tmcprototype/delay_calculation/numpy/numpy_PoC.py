import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures

# Calculate 5th order polynomial coefficients​
antenna_delay_list = []
x = np.array([-25, -15, -5, 5, 15, 25])

# 6 delay values for antenna 1 around the interval 10 seconds
t0_delay = -0.00000050178708094610  # Delay at t0 - 25
t1_delay = -0.00000050179250923286  # Delay at t0 - 15
t2_delay = -0.00000050179804711394  # Delay at t0 - 5
t3_delay = -0.00000050180366432404  # Delay at t0 + 5
t4_delay = -0.00000050180939400960  # Delay at t0 + 15
t5_delay = -0.00000050181521815249  # Delay at t0 + 25

antenna_delay_list.append(t0_delay)
antenna_delay_list.append(t1_delay)
antenna_delay_list.append(t2_delay)
antenna_delay_list.append(t3_delay)
antenna_delay_list.append(t4_delay)
antenna_delay_list.append(t5_delay)

y = np.array(antenna_delay_list)

# smoothing factor (s) is 0 (implicit for InterpolatedUnivariateSpline)
# Degree of the smoothing spline (k) is 5 as the coefficients of 5th order are needed.
sp = InterpolatedUnivariateSpline(x, y, k=5)

# Old NumPy version
np1 = np.polyfit(x, y, 5)
# New NumPy version
np2 = np.polynomial.Polynomial.fit(x, y, 5)
print("np2.shape", type(np2))
# New NumPy version with restricted domain
# domain = [-5, 5] seems like an interesting option to explore here
np3 = np.polynomial.Polynomial.fit(x, y, 5, domain=[-5, 5])

print('SciPy spline coefs =', sp.get_coeffs())
# Coefficients in order of increasing degree...
print('NumPy old poly     =', np1[::-1])
print('NumPy old poly -------------------    =', np1)
print('NumPy new poly     =', np2.coef)
print('NumPy new poly v2  =', np3.coef)

# Evaluate the versions at the middle timestamp
print('SciPy spline poly at t0 =', sp(0))
print('NumPy old poly at t0    =', np.polyval(np1, 0))
print('NumPy new poly at t0    =', np2(0))
print('NumPy new poly v2 at t0 =', np3(0))

plt.plot(x, sp.get_coeffs(), 'm')
# plt.plot(x, np1[::-1], 'b')
plt.plot(x, np2.coef, 'c')
# plt.plot(x, np3.coef, 'y')

plt.show()