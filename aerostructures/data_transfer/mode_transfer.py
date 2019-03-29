# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

'''
ExplicitComponent which takes the matrix of normal modes on a grid and gives the matrix of normal modes on another grid according to the interpolation matrix H
'''


class ModeTransfer(ExplicitComponent):

    def __init__(self, nr, nm, N, BC):
        super(ModeTransfer, self).__init__()

        # Number of points of the source grid
        self.nr = nr

        # Number of points of the target grid
        self.nm = nm

        # Number of modes
        self.N = N

        # Table indicating whether a DOF in the target model is either free (1) or constrained (0)
        self.BC = BC

    def setup(self):

        # Interpolation matrix H (xm = H xr)
        self.add_input('H', val=np.zeros((self.nm, self.nr)))

        # Matrix of source normal modes
        self.add_input('Phi_r', val=np.zeros((self.nr, 6*self.N)))

        # Matrix of target normal modes
        self.add_output('Phi_m', val=np.zeros((self.nm, 6*self.N)))

    def compute(self, inputs, outputs):

        Phi_r = inputs['Phi_r']

        H = inputs['H']

        N = self.N

        BC = self.BC

        # Apply the interpolation matrix to obtain displacements on target grid
        Phi_m = H.dot(Phi_r)

        # Apply the known boundary conditions to the target model displacements
        Phi_m = np.multiply(Phi_m, np.tile(BC, N))

        outputs['Phi_m'] = Phi_m
