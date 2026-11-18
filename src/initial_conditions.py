import numpy as np

def initial(x, profile="packet", mode=1):
    x = np.mod(x, 1.0)
    if profile == "sine": return np.sin(2*np.pi*mode*x)
    if profile == "packet": return np.exp(-10*(1-np.cos(2*np.pi*x)))
    if profile == "square": return ((x >= .25) & (x < .5)).astype(float)
    raise ValueError("unknown profile")
