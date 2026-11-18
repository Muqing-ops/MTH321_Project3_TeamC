import numpy as np

def grid(n):
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 4:
        raise ValueError("N must be an integer >= 4")
    return np.arange(n) / n, 1.0 / n

def time_grid(n, T, C=0.5, a=1.0):
    grid(n)
    if not np.isfinite([T, C, a]).all() or T < 0 or not 0 < C <= 1 or a == 0:
        raise ValueError("finite T >= 0, 0 < C <= 1 and nonzero speed required")
    steps = max(1, int(np.ceil(T * abs(a) * n / C)))
    return steps, T / steps, a * T * n / steps
