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

    def __init__(self, na, ns):
        super(ModeTransfer, self).__init__()

        # Number of points of the aerodynamic grid
        self.na = na

        # Number of nodes of the structural mesh on the outer skin
        self.ns = ns

        # Interpolation matrix H (xa = H xs)
        self.add_param('H', val=np.zeros((self.na, self.ns)))

        # Nodal displacements of the outer surface
        self.add_param('u', val=np.zeros((self.ns, 3)))

        # Displacements of the aerodynamic grid points
        self.add_output('delta', val=np.zeros((self.na, 3)))

    def solve_nonlinear(self, params, unknowns, resids):

        u = params['u']

        H = params['H']

        # Apply the interpolation matrix to obtain the aerodynamic points displacements
        unknowns['delta'] = H.dot(u)
