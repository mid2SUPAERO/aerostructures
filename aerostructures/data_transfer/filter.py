# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which takes the nodal displacements and gives the displacements of
the aerodynamic points
'''
class Filter(Component):


    def __init__(self, ns, fidelity):
        super(Filter, self).__init__()
        
        #Number of nodes of the structural mesh on the outer skin
        self.ns = ns
        
        #Displacement field from the structures component
        self.add_param('u', val=np.zeros((self.ns, 3)))

        #Displacement field from the Lo-Fi component
        self.add_param('ul', val=np.zeros((self.ns, 3)))

        #Displacements after decision
        self.add_output('us', val=np.zeros((self.ns, 3)))
        
        #Aux variable
        if fidelity == 'high':
            self.aux = 1
        else:
            self.aux = 0


    def solve_nonlinear(self, params, unknowns, resids):
        u = params['u']
        #print(u)
        ul = params['ul']
        #print(ul)
        #if (u == np.zeros((len(u),3))).all() is True:
        if self.aux == 0:
            unknowns['us'] = ul
            self.aux = 1
            print('Se envió el vector ul')
         
        else:
            unknowns['us'] = u
            print('Se envió el vector u')
            

        
