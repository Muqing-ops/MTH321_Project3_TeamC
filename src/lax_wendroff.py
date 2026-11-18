import numpy as np

def step(u, c):
    return u - .5*c*(np.roll(u,-1)-np.roll(u,1)) + .5*c*c*(np.roll(u,-1)-2*u+np.roll(u,1))
