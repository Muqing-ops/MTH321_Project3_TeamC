import numpy as np
from .upwind import step as upwind
from .lax_wendroff import step as lw
from .tvd import step as tvd
from .grid import time_grid

METHODS={"upwind": upwind, "lw": lw, "mc": tvd, "minmod": lambda u,c: tvd(u,c,"minmod")}

def evolve(u0, method, T, C=.5, a=1., record=False):
    u=np.array(u0,dtype=float,copy=True)
    if u.ndim != 1 or len(u)<4 or not np.isfinite(u).all(): raise ValueError("finite 1D state of length >=4 required")
    if method not in METHODS: raise ValueError("unknown method")
    steps,dt,c=time_grid(len(u),T,C,a)
    fn=METHODS[method]
    history=[u.copy()] if record else None
    for _ in range(steps):
        u=fn(u,c)
        if record: history.append(u.copy())
    return u, dict(steps=steps,dt=dt,C=c,T=T,N=len(u),a=a), history
