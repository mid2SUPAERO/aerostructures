# -*- coding: utf-8 -*-
"""
@author: © Gilberto Ruiz Jiménez

"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component that imports the displacement field from the Lo-Fi level to the Hi-Fi level when needed, and if not
keeps the displacement field from the previous iteration
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
        
        #Aux variables
        self.ul_old = np.zeros((self.ns,3))
        
        #Fidelity level
        self.fidelity = fidelity
        
        if self.fidelity == 'high':
            self.aux = 1
        else:
            self.aux = 0


    def solve_nonlinear(self, params, unknowns, resids):
        u = params['u']
        ul = params['ul']
                
        #Changes the value of aux when a new iteration of the optimizer started
        if self.aux == 1 and np.array_equal(self.ul_old, ul) == False: 
            if self.fidelity == 'high':
                self.aux = 1
            else:
                self.aux = 0
                
        #Changes fidelities if needed
        if self.aux == 0:
            unknowns['us'] = ul
            self.ul_old = np.copy(ul)  
            self.aux = 1
            print('::::::::Fidelity changed, displacement field imported::::::::')
            
        #Keeps current displacement field during the same MDA loop
        else:
            unknowns['us'] = u
            print('::::::::Displacement field kept from previous iteration::::::::')
            
            

