# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which takes the forces at the aerodynamic points and gives the
nodal forces
'''
class LoadTransfer(Component):


    def __init__(self, na, ns):
        super(LoadTransfer, self).__init__()

        #Number of points of the aerodynamic grid
        self.na = na

        #Number of nodes of the structural mesh on the outer skin
        self.ns = ns

        #Interpolation matrix H (xa = H xs)
        self.add_param('H', val=np.zeros((self.na, self.ns)))

        #Forces on the aerodynamic grid points
        self.add_param('f_a', val=np.zeros((self.na, 3)))

        #Nodal forces of the outer surface
        self.add_output('f_node', val=np.zeros((self.ns, 3)))


    def solve_nonlinear(self, params, unknowns, resids):

        f_a = params['f_a']

        H = params['H']

        #Apply the transpose of the displacement interpolation matrix to obtain the nodal forces
        unknowns['f_node'] = np.transpose(H).dot(f_a)
