import numpy as np
import time

np.random.seed(10)

rate = 200

# Define the pulse shape: a simple gaussian
def pulse_shape(t, t0=5., a=12., sigma=1.):
    return np.exp(-((t - t0)/(2.*sigma))**2) * a

# Digitize to 8 bit plus saturation
resolution = 2**8
digitization_bins = np.linspace(0, 12, resolution+1)
digitization_step = digitization_bins[1] - digitization_bins[0]
def digitize(y):
    y = np.digitize(y, digitization_bins)
    y = np.clip(y, a_min=1, a_max=resolution)
    return y - 1


while True:
    t = np.linspace(0, 10, 101)
    a = float(0.5 + np.random.exponential(scale=5.))
    y = pulse_shape(t, a=a)
    y = digitize(y)/10
    print("{0:.4f} ".format(a) + " ".join(["{0}".format(yi) for yi in y]))
    time.sleep(1./rate)
