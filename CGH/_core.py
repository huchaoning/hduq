import numpy as np
from numpy import pi, sqrt, inf, arctan

from scipy.special import hermite, laguerre
from scipy.interpolate import interp1d

from os import path

from dataclasses import dataclass


__all__ = ['SLM', 'HG', 'LG', 'LASER']


def _fx2():
    fx = np.load(path.join(path.dirname(__file__), 'fx2.npy'))
    return interp1d(np.linspace(0, 1, 801), fx)


def _I(arr):
    temp = np.square(np.abs(arr))
    temp = temp / temp.max()
    return temp


class SLM:
    device = 'HoloEye, PLUTO-2-NIR-011'

    pixel_size = 8
    resolution = (1920, 1080)
    
    x, y = np.meshgrid(
           np.arange(-resolution[0]/2, resolution[0]/2) * pixel_size,
          -np.arange(-resolution[1]/2, resolution[1]/2) * pixel_size)


@dataclass
class _Mode:
    n: int
    m: int

    def __post_init__(self):
        valid = all(isinstance(x, int) and x >= 0 for x in (self.n, self.m))
        if not valid:
            raise ValueError('orders must be positive integers')


class HG(_Mode):
    pass


class LG(_Mode):
    pass


class LASER:
    def __init__(self, wavelength, beam_waist, mode):
        self.wavelength = wavelength
        self.wave_number = 2 * pi / self.wavelength
        self.beam_waist = beam_waist
        self.rayleigh_range = (pi * self.beam_waist**2) / self.wavelength
    
        if isinstance(mode, (HG, LG)):
            self.mode = mode
        else:
            raise TypeError('mode must be HG or LG')


    def beam_size(self, z):
        return self.beam_waist * sqrt(1 + (z / self.rayleigh_range)**2)


    def gouy_phase(self, z):
        return arctan(z / self.rayleigh_range)


    def wave_radius_of_curvature(self, z):
        return inf if z==0 else z * (1 + (self.rayleigh_range / z)**2)


    def amplitude(self, x, y, z):
        rho = x**2 + y**2
        w = self.beam_size(z)

        if isinstance(self.mode, HG):
            n, m = self.mode.n, self.mode.m
            hx, hy= hermite(n)(sqrt(2)*x/w), hermite(m)(sqrt(2)*y/w)
            amplitude = hx*hy*np.exp(-rho/(w**2))
            return amplitude / np.abs(amplitude).sum()

        elif isinstance(self.mode, LG):
            raise TypeError('LG is not supported yet')


    def phase(self, x, y, z):
        rho = x**2 + y**2
        xi = self.gouy_phase(z)
        k = self.wave_number
        r = self.wave_radius_of_curvature(z)

        if isinstance(self.mode, HG):
            n, m = self.mode.n, self.mode.m
            return np.exp(1j*(k*(rho**2/(2*r)+z)-xi*(n+m+1)))

        elif isinstance(self.mode, LG):
            raise TypeError('LG is not supported yet')


    def complex_amplitude(self, x, y, z):
        return self.amplitude(x, y, z) * self.phase(x, y, z)





# def superposition(mode_1, mode_2, split=50):
#     return mode_1*np.exp(2j*pi*y*split/(v*p))+mode_2*np.exp(-2j*pi*y*split/(v*p))


# def gen(complex_amplitude=None, method=2, nx=500, ny=0): 
#     f = _fx2()
#     a = np.abs(complex_amplitude) / np.abs(complex_amplitude).max()
#     phi = np.angle(complex_amplitude)

#     if method == 1:
#         img = phi + f(a) * np.sin(phi + (2*pi*(x*nx/(h*p)+y*ny/(v*p))))
#     elif method == 2:
#         img = f(a) * np.sin(phi + (2*pi*(x*nx/(h*p)+y*ny/(v*p))))

#     return (_I(img) * 255).astype(np.uint8)
