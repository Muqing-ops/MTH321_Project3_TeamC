from .initial_conditions import initial

def exact(x, t, profile="packet", a=1.0, mode=1):
    return initial((x-a*t) % 1.0, profile, mode)
