# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which takes the aerodynamic jig mesh coordinates and gives the coordinates of the structural mesh
'''
class AeroHiFiMesher(Component):


    def __init__(self, ngeom_unique, na, na_unique):
        super(AeroHiFiMesher, self).__init__()

        #Number of points of the grid defining the geometry
        self.ngeom_unique = ngeom_unique

        #Number of points of the HiFi surface mesh
        self.na = na

        #Number of unique points of the HiFi surface mesh
        self.na_unique = na_unique

        #Interpolation matrix D (xa = D xg)
        self.add_param('D', val=np.zeros((self.na, self.ngeom_unique)))

        #Coordinates of the aerodynamic jig mesh
        self.add_param('apoints_coord_unique', val=np.zeros((self.ngeom_unique, 3)))

        #Coordinates of the HiFi surface mesh
        self.add_output('jig_surface_coord', val=np.zeros((self.na, 3)))

        #Unique coordinates of the HiFi surface mesh
#        self.add_output('jig_surface_coord_unique', val=np.zeros((self.na_unique, 3)))


    def solve_nonlinear(self, params, unknowns, resids):

        apoints_coord_unique = params['apoints_coord_unique']
        print('apoints_coord_unique_shape='+str(apoints_coord_unique.shape))
        
        np.savetxt('apoints_coord_unique', apoints_coord_unique)

        D = params['D']
        print('D_shape='+str(D.shape))
        print('unique_lines_D='+str(np.unique(D, axis=0).shape))

        #Apply the interpolation matrix to obtain the aerodynamic points displacements
        jig_surface_coord = D.dot(apoints_coord_unique)
        print('jig_surface_coord='+str(jig_surface_coord.shape))
        np.savetxt('jig_surface_coord', jig_surface_coord)

        #Remove duplicates
#        jig_surface_coord_unique_, ind = np.unique(jig_surface_coord, axis=0, return_index=True)
#		
#        jig_surface_coord_unique = jig_surface_coord_unique_[np.argsort(ind)]

        #Set unknowns value
        unknowns['jig_surface_coord'] = jig_surface_coord
#        print(unknowns['jig_surface_coord_unique'].shape,jig_surface_coord_unique.shape)

#        unknowns['jig_surface_coord_unique'] = jig_surface_coord_unique
