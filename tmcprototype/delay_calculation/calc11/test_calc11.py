#!/usr/bin/env python3

import numpy as np
from calc11 import almacalc
import matplotlib.pyplot as plt

nant = 1
ntimes = 60

refx = 1000.0
refy = 1299.0
refz = 6380000.0
antx = np.array([1500.0])
anty = np.array([1500.0])
antz = np.array([6380000.0])
temp = np.array([0.0])
pressure = np.array([0.0])
humidity =  np.array([0.0])

mjd = np.array([58701.45833333349, 58701.45902777789, 58701.459722222295, 58701.4604166667, 58701.4611111111, 58701.461805555504, 58701.46249999991, 58701.46319444431, 58701.46388888871, 58701.464583333116, 58701.465277777985, 58701.46597222239, 58701.46666666679, 58701.467361111194, 58701.4680555556, 58701.46875, 58701.4694444444, 58701.470138888806, 58701.47083333321, 58701.47152777761, 58701.472222222015, 58701.472916666884, 58701.47361111129, 58701.47430555569, 58701.47500000009, 58701.475694444496, 58701.4763888889, 58701.4770833333, 58701.477777777705, 58701.47847222211, 58701.47916666651, 58701.479861110914, 58701.48055555578, 58701.481250000186, 58701.48194444459, 58701.48263888899, 58701.483333333395, 58701.4840277778, 58701.4847222222, 58701.485416666605, 58701.48611111101, 58701.48680555541, 58701.487499999814, 58701.48819444422, 58701.488888889086, 58701.48958333349, 58701.49027777789, 58701.490972222295, 58701.4916666667, 58701.4923611111, 58701.493055555504, 58701.49374999991, 58701.49444444431, 58701.49513888871, 58701.495833333116, 58701.496527777985, 58701.49722222239, 58701.49791666679, 58701.498611111194, 58701.4993055556])

# mjd = np.array([58701.45833333349, 58701.45902777778])
ra  = np.array([0.0442] * ntimes)
dec = np.array([1.5580] * ntimes)
print("ra: ", ra)
print("dec: ", dec)

ssobj = np.zeros(ntimes, dtype=bool)
print("ssobj: ", ssobj)
dx = np.zeros(ntimes)
dy = np.zeros(ntimes)
dut = np.zeros(ntimes)
leapsec = 37.0
axisoff = np.zeros(nant)
sourcename = ['P'] * ntimes
jpx_de421 = 'data/DE421_little_Endian'

geodelay, drydelay, wetdelay = almacalc(refx, refy, refz, antx, anty,
                                        antz, temp, pressure,
                                        humidity, mjd, ra, dec, ssobj,
                                        dx, dy, dut, leapsec, axisoff,
                                        sourcename, jpx_de421)

geodelay_plot = []
for i in range(0,60):
    geodelay_plot.append(geodelay[0][i])

geodelay_plot_array = np.array(geodelay_plot)

plt.plot(mjd, geodelay_plot_array)
plt.show()

print("---------------------------------------------------------------------")
print('geodelay:')
print(geodelay)
print("---------------------------------------------------------------------")
print('drydelay:')
print(drydelay)
print("---------------------------------------------------------------------")
print('wetdelay:')
print(wetdelay)
print("---------------------------------------------------------------------")

print("geodelay shape", geodelay.shape)
print(geodelay_plot_array.shape)
#print("mjd shape", mjd.shape)
