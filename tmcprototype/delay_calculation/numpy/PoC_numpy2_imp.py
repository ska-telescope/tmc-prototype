import numpy as np
import matplotlib.pyplot as plt

# Sample delay every second for 60 seconds
seconds = np.arange(0, 61)
delay = np.array([2.190179865006205e-06, 2.190197787753078e-06, 2.190213221863872e-06, 2.190231144613648e-06, 2.1902490673647112e-06, 2.190266990117063e-06, 2.1902849128707015e-06, 2.1903028356256277e-06, 2.1903207583818417e-06, 2.1903361925041464e-06, 2.190354115263263e-06, 2.1903720380236668e-06, 2.1903899607853578e-06, 2.1904078835483354e-06, 2.1904258063126e-06, 2.190441240444798e-06, 2.190459163211965e-06, 2.1904770859804197e-06, 2.1904950087501605e-06, 2.190512931521188e-06, 2.1905308542935028e-06, 2.1905488607927833e-06, 2.1905642949369918e-06, 2.1905822177140916e-06, 2.190600140492477e-06, 2.1906180632721502e-06, 2.190635986053109e-06, 2.190653908835354e-06, 2.1906693429894522e-06, 2.1906872657745976e-06, 2.19070518856103e-06, 2.190723111348748e-06, 2.190741034137752e-06, 2.1907589569280424e-06, 2.1907768797196184e-06, 2.190792313885218e-06, 2.190810236679694e-06, 2.1908281594754553e-06, 2.1908460822725027e-06, 2.1908640050708355e-06, 2.1908820116071957e-06, 2.1908974457831857e-06, 2.190915368586301e-06, 2.1909332913907e-06, 2.190951214196386e-06, 2.190969137003357e-06, 2.190987059811613e-06, 2.191004982621154e-06, 2.1910204168086414e-06, 2.1910383396210807e-06, 2.1910562624348053e-06, 2.191074185249815e-06, 2.191092108066109e-06, 2.1911101146280014e-06, 2.1911255488258745e-06, 2.191143471646949e-06, 2.1911613944693077e-06, 2.191179317292951e-06, 2.191197240117879e-06, 2.191215162944091e-06, 2.1912305971518444e-06])

# SET 1
# 6 delay values, one every 10 seconds
x = np.arange(0, 60, 10)    # [0, 10, 20, 30, 40, 50]
y = delay[x]
# Fit polynomial to values over 50-second range
poly = np.polynomial.Polynomial.fit(x, y, 5)
# Now interpolate delays between 20 and 30 seconds by evaluating polynomial
x_eval = np.arange(20, 31)   # [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
y_eval = poly(x_eval)        # here we evaluate the polynomial
coeff_sum = poly.convert().coef[0] + (poly.convert().coef[1] * (25)) + (poly.convert().coef[2] * (25**2)) + (poly.convert().coef[3] * (25 ** 3)) + (poly.convert().coef[4] * (25 ** 4)) + (poly.convert().coef[5] * (25 ** 5))
plt.figure()
# Indicate region of interest where CSP needs delay values
plt.plot(seconds, delay, 'y', lw=2, label='truth', linewidth=4.0)
plt.plot(x, y, 'bo', label='input to fitter', markersize = 8)
plt.plot(x_eval, y_eval, 'm--', label='interpolation 1', linewidth=4.0)

# SET 2
# 6 delay values, one every 10 seconds
x_2 = np.arange(10,70,10) # [10, 20, 30, 40, 50, 60]
y_2 = delay[x_2]
# Fit polynomial to values over 50-second range
poly = np.polynomial.Polynomial.fit(x_2, y_2, 5)
# Now interpolate delays between 20 and 30 seconds by evaluating polynomial
x_eval = np.arange(30, 41)   # [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
y_eval = poly(x_eval)        # here we evaluate the polynomial
plt.plot(x_2, y_2, 'ro', label='input to fitter', markersize = 6)
plt.plot(x_eval, y_eval, 'g--', label='interpolation 2', linewidth=4.0)

plt.xlabel('Time (seconds)')
plt.ylabel('Delay value')
# plt.axis([0, 60, 0, 1.4])
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05) , ncol=3)
plt.show()
