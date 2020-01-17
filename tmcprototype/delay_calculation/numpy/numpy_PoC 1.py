import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures

# Calculate 5th order polynomial coefficients​
antenna_delay_list = []
# x = np.array(list(range(60)))
x = [0, 10, 20, 30, 40, 50]

# 6 delay values for antenna 1 around the interval 10 seconds
antenna_delay_list = [2.190179865006205e-06, 2.1912305971518444e-06, 2.1922844095962797e-06, 2.1933361582014256e-06, 2.1943860112334824e-06, 2.195436374122465e-06, 2.196484758941048e-06, 2.1975336548655813e-06, 2.198580573993878e-06, 2.199625516972156e-06, 2.2006735454663226e-06, 2.201717026545569e-06, 2.2027611059499662e-06, 2.2038057002179245e-06, 2.2048458330701756e-06, 2.2058889704443555e-06, 2.206927647647454e-06, 2.207966842143005e-06, 2.2090065545183005e-06, 2.21004429696486e-06, 2.21108007008855e-06, 2.212116362872677e-06, 2.2131482836037007e-06, 2.21418312911981e-06, 2.215213519307492e-06, 2.216244431492053e-06, 2.217275866244901e-06, 2.2183028474207893e-06, 2.2193303523128436e-06, 2.220355893131547e-06, 2.2213819587974248e-06, 2.222406061518145e-06, 2.223428201852946e-06, 2.22444829554434e-06, 2.2254690010930493e-06, 2.2264876610364417e-06, 2.227504360730122e-06, 2.228519100712962e-06, 2.229534369889904e-06, 2.2305476804298064e-06, 2.2315589478302937e-06, 2.232568342642501e-06, 2.2335756952951526e-06, 2.2345835797324235e-06, 2.235589508078724e-06, 2.236593395659749e-06, 2.237595328098882e-06, 2.238595305894153e-06, 2.2395958179849804e-06, 2.2405942911361698e-06, 2.2415883226069542e-06, 2.242582889803751e-06, 2.243575419359573e-06, 2.2445684855834287e-06, 2.2455571119456277e-06, 2.2465437019288805e-06, 2.24753082995995e-06, 2.248513433879069e-06, 2.2494965767285268e-06, 2.250477770407318e-06]

y = np.array([antenna_delay_list[0], antenna_delay_list[10],antenna_delay_list[20], antenna_delay_list[30], antenna_delay_list[40], antenna_delay_list[50]])

# smoothing factor (s) is 0 (implicit for InterpolatedUnivariateSpline)
# Degree of the smoothing spline (k) is 5 as the coefficients of 5th order are needed.
sp = InterpolatedUnivariateSpline(x, y, k=5)

# Old NumPy version
np1 = np.polyfit(x, y, 5)
print("lenghth np1: ", len(np1))
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
# print('SciPy spline poly at t0 =', sp(0))
print('NumPy old poly at t0    =', np.polyval(np1, 0))
print('NumPy new poly at t0    =', np2(0))
print('NumPy new poly v2 at t0 =', np3(0))

plt.plot(x, sp.get_coeffs(), 'm')
plt.plot(x, np1[::-1], 'b')
plt.plot(x, np2.coef, 'c')
plt.plot(x, np3.coef, 'y')

plt.show()