# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which takes the matrix of normal modes on a grid and gives the matrix of normal modes on another grid according to the interpolation matrix H
'''

class ModeTransfer(Component):

    def __init__(self, nr, nm, N):
        super(ModeTransfer, self).__init__()

        # Number of points of the source grid
        self.nr = nr

        # Number of points of the target grid
        self.nm = nm
        
        #Number of modes
        self.N = N

        # Interpolation matrix H (xm = H xr)
        self.add_param('H', val=np.zeros((self.nm, self.nr)))

        # Matrix of source normal modes
        self.add_param('Phi_r', val=np.zeros((self.nr, 3)))

        # Matrix of target normal modes
        self.add_output('delta', val=np.zeros((self.nm, 3)))

    def solve_nonlinear(self, params, unknowns, resids):

        u = params['u']

        H = params['H']

        # Apply the interpolation matrix to obtain the aerodynamic points displacements
        unknowns['delta'] = H.dot(u)
