import numpy as np

def limited_jump(backward, forward, limiter="mc"):
    """phi(backward/forward)*forward without division or epsilon bias.

    A zero forward jump returns zero, including the 0/0 case. Opposite
    signs return zero. This is exactly minmod/MC limiting for finite data.
    """
    same = np.sign(backward) == np.sign(forward)
    if limiter == "minmod": size = np.minimum(abs(backward), abs(forward))
    elif limiter == "mc": size = np.minimum(np.minimum(2*abs(backward),2*abs(forward)), .5*abs(backward+forward))
    else: raise ValueError("unknown limiter")
    return np.where(same, np.sign(forward)*size, 0.0)

def flux(u, c, limiter="mc"):
    """Dimensionless flux f/a for positive velocity; c in [0,1]."""
    return u + .5*(1-c)*limited_jump(u-np.roll(u,1), np.roll(u,-1)-u, limiter)

def step(u, c, limiter="mc"):
    if c < 0: return step(u[::-1], -c, limiter)[::-1]
    f = flux(u,c,limiter)
    return u-c*(f-np.roll(f,1))

def rhs(t, u, n, limiter="mc"):
    f=flux(u,0,limiter)
    return -n*(f-np.roll(f,1))
