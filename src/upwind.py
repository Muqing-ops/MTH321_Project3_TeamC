import numpy as np

def step(u, c):
    if c >= 0: return u - c*(u-np.roll(u, 1))
    return u - c*(np.roll(u, -1)-u)
