# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which takes the aerodynamic jig mesh coordinates and gives the coordinates of the structural mesh
'''
class StructureMesher(Component):


    def __init__(self, na_unique, node_id, node_id_all):
        super(StructureMesher, self).__init__()

        #Identification number of the outer surface nodes
        self.node_id = node_id

        #Identification number of all the structural nodes
        self.node_id_all = node_id_all

        #Number of points of the aerodynamic grid
        self.na_unique = na_unique

        #Number of nodes of the structural mesh on the outer skin
        self.ns = len(node_id)

        #Number of nodes of the structural mesh (total)
        self.ns_all = len(node_id_all)

        #Interpolation matrix G (xs = G xa)
        self.add_param('G', val=np.zeros((self.ns_all, self.na_unique)))

        #Coordinates of the aerodynamic jig mesh
        self.add_param('apoints_coord_unique', val=np.zeros((self.na_unique, 3)))

        #Coordinates of the structure mesh (surface only)
        self.add_output('node_coord', val=np.zeros((self.ns, 3)))

        #Coordinates of the structure mesh (all nodes)
        self.add_output('node_coord_all', val=np.zeros((self.ns_all, 3)))


    def solve_nonlinear(self, params, unknowns, resids):

        apoints_coord_unique = params['apoints_coord_unique']

        G = params['G']

        node_id = self.node_id

        node_id_all = self.node_id_all

        node_coord = []

        #Apply the interpolation matrix to obtain the aerodynamic points displacements
        node_coord_all = G.dot(apoints_coord_unique)

        #Set value of the coordinates of the surface nodes
        for i in range(len(node_id_all)):
            if node_id_all[i] in node_id:
                node_coord.append(node_coord_all[i])

        #Store node_coord as array
        node_coord = np.asarray(node_coord)

        #Set unknowns value
        unknowns['node_coord_all'] = node_coord_all
        unknowns['node_coord'] = node_coord
