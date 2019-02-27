# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from aerostructures.data_transfer.rbf_poly_bias import Rbf_poly_bias

from openmdao.api import ExplicitComponent

#ExplicitComponent which gives the interpolation matrix (H) given the aerodynamics and structural meshes
class Interpolation(ExplicitComponent):


    def setup(self, na, ns, **kwargs):
        #Number of points of the aerodynamic grid
        self.na = na

        #Number of nodes of the structural mesh on the outer skin
        self.ns = ns

        #RBF function type
        self.function_type = kwargs.pop('function', None)

        #Epsilon parameter of the RBF functions
        self.epsilon = kwargs.pop('epsilon', None)

        #Norm bias
        self.bias = kwargs.pop('bias', None)

        #Aerodynamic grid points coordinates
        self.add_input('apoints_coord', val=np.zeros((self.na, 3)))

        #Coordinates of the structural nodes on the outer surface
        self.add_input('node_coord', val=np.zeros((self.ns, 3)))

        #Interpolation matrix H (xa = H xs)
        self.add_output('H', val=np.zeros((self.na, self.ns)))


    def compute(self, inputs, outputs):

        apoints_coord = inputs['apoints_coord']

        node_coord = inputs['node_coord']

        #Create an RBF interpolation with polynomial terms from the structural nodes and aerodynamic points coordinates
        inter = Rbf_poly_bias(node_coord[:, 0], node_coord[:, 1], node_coord[:, 2], apoints_coord[:, 0], apoints_coord[:, 1], apoints_coord[:, 2], function=self.function_type, epsilon=self.epsilon, bias=self.bias)

        #Set the interpolation matrix (H) as an output
        outputs['H'] = inter.H
