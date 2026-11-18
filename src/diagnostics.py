import numpy as np

def norms(error):
    e=abs(error)
    return dict(L1=float(e.mean()), L2=float(np.sqrt(np.mean(e*e))), Linf=float(e.max()))

def diagnostics(u):
    return dict(mass=float(u.mean()), TV=float(abs(np.roll(u,-1)-u).sum()), minimum=float(u.min()), maximum=float(u.max()), overshoot=float(max(0,u.max()-1)), undershoot=float(max(0,-u.min())), transition_cells=int(np.count_nonzero((u>.1)&(u<.9))), transition_width=float(np.count_nonzero((u>.1)&(u<.9))/len(u)))

def mode_coefficient(u, mode=1):
    return np.mean(u*np.exp(-2j*np.pi*mode*np.arange(len(u))/len(u)))
