# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

'''
ExplicitComponent which takes the forces at the aerodynamic points and gives the
nodal forces
'''
class LoadTransfer(ExplicitComponent):


    def setup(self, na, ns):
        #Number of points of the aerodynamic grid
        self.na = na

        #Number of nodes of the structural mesh on the outer skin
        self.ns = ns

        #Interpolation matrix H (xa = H xs)
        self.add_input('H', val=np.zeros((self.na, self.ns)))

        #Forces on the aerodynamic grid points
        self.add_input('f_a', val=np.zeros((self.na, 3)))

        #Nodal forces of the outer surface
        self.add_output('f_node', val=np.zeros((self.ns, 3)))


    def compute(self, inputs, outputs):

        f_a = inputs['f_a']

        H = inputs['H']

        #Apply the transpose of the displacement interpolation matrix to obtain the nodal forces
        outputs['f_node'] = np.transpose(H).dot(f_a)
