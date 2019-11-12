# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which takes the aerodynamic displacements and gives the displacements of the geometric surface
'''
class AeroSurfTransfer(Component):


    def __init__(self, na, na_unique, ngeom):
        super(AeroSurfTransfer, self).__init__()
        
        #Number of points of the HiFi surface mesh
        self.na = na
        
        #Number of unique points of the HiFi surface mesh
        self.na_unique = na_unique

        #Number of points of the grid defining the geometry
        self.ngeom = ngeom

        #Interpolation matrix F (xg = F xa)
        self.add_param('F', val=np.zeros((self.ngeom, self.na_unique)))
        
        #Displacements of the HiFi surface mesh points
        self.add_param('delta', val=np.zeros((self.na, 3)))

        #Displacements transferred to the geometric surface mesh
        self.add_output('delta_geom', val=np.zeros((self.ngeom, 3)))


    def solve_nonlinear(self, params, unknowns, resids):

        delta = params['delta']
        
        #Displacements of the HiFi unique surface mesh points        
        delta_unique, ind = np.unique(delta, axis=0, return_index=True)
        
        delta_unique = delta_unique[np.argsort(ind)]

        F = params['F']

        #Apply the interpolation matrix to obtain the aerodynamic points displacements
        delta_geom = F.dot(delta_unique)

        #Set unknowns value
        unknowns['delta_geom'] = delta_geom
