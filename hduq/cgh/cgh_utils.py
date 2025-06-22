import numpy as np
from .core import *



def line(modes_num, x_scale=1, y_scale=1):
    nx = np.array([500] * modes_num).ravel() if modes_num != 1 else 500
    ny = np.linspace(-50, 50, modes_num) if modes_num != 1 else 0
    return np.array([nx * x_scale, ny * y_scale])



def arc(modes_num, x_scale=1, y_scale=1):
    angle_rad = np.deg2rad(45)
    theta = np.linspace(-angle_rad/2, angle_rad/2, modes_num)
    radius = 500
    nx = radius * np.cos(theta)
    ny = radius * np.sin(theta) 
    return np.array([nx * x_scale, ny * y_scale])



def hg_mat(max_n, max_m):
    modes = np.empty((max_n+1, max_m+1), dtype=object)
    for n in range(max_n):
        for m in range(max_m):
            modes[n, m] = HG(n, m)
    return modes



def pm_mat(max_n, max_m):
    modes = [HG(n, m) for n in range(max_n+1) for m in range(max_m+1)]
    size = len(modes)
    pm_modes = np.empty((size, size), dtype=object)
    for i in range(size):
        for j in range(i, size):
            if i != j:
                pm_modes[i, j] = modes[i] + modes[j]
                pm_modes[j, i] = modes[i] - modes[j]
    return pm_modes




def preset_cgh(*modes, sigma, dist, x_scale=1, y_scale=1):
    cgh = CGH(sigma)
    if dist == 'v_line':
        cgh.add_modes(modes, *line(len(modes), x_scale, y_scale))
    elif dist == 'h_line':
        cgh.add_modes(modes, *line(len(modes), x_scale, y_scale)[::-1, ...])
    elif dist == 'v_arc':
        cgh.add_modes(modes, *arc(len(modes), x_scale, y_scale))
    elif dist == 'h_arc':
        cgh.add_modes(modes, *arc(len(modes), x_scale, y_scale)[::-1, ...])

    cgh.cal()
    return cgh
