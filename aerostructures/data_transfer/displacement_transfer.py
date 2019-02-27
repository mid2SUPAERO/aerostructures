# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

'''
Component which takes the nodal displacements and gives the displacements of
the aerodynamic points
'''
class DisplacementTransfer(ExplicitComponent):

    def __init__(self, na, ns):
        super(DisplacementTransfer, self).__init__()

        #Number of points of the aerodynamic grid
        self.na = na

        #Number of nodes of the structural mesh on the outer skin
        self.ns = ns

    def setup(self):
        #Interpolation matrix H (xa = H xs)
        self.add_input('H', val=np.zeros((self.na, self.ns)))

        #Nodal displacements of the outer surface
        self.add_input('u', val=np.zeros((self.ns, 3)))

        #Displacements of the aerodynamic grid points
        self.add_output('delta', val=np.zeros((self.na, 3)))


    def compute(self, inputs, outputs):

        u = inputs['u']

        H = inputs['H']

        #Apply the interpolation matrix to obtain the aerodynamic points displacements
        outputs['delta'] = H.dot(u)
