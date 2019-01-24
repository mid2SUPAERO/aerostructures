# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from aerostructures.number_formatting.is_number import isfloat

class AeroProblemParams:
    #Jig shape geometry
    jig_shape = 'aero_template.wgs'


    def __init__(self):

        #Dictionary containing the structural parameters
        self.aero_params = self.get_aero_params()

        #Aerodynamic mesh points coordinates
        self.apoints_coord = self.aero_params['apoints_coord']

        #Unique aerodynamic mesh points coordinates
        self.apoints_coord_unique = self.aero_params['apoints_coord_unique']


    #Function that returns the aerodynamic points coordinates
    def get_aero_params(self):

        apoints_coord = []

        #Write the aerodynamic grid points coordinates into a list (excluding the root section)
        with open(self.jig_shape) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for line in lines:
                if all(isfloat(item) for item in line):
                    if len(line) == 3:
                        apoints_coord.append([float(line[0]), float(line[1]), float(line[2])])
                    if len(line) == 6:
                        apoints_coord.append([float(line[0]), float(line[1]), float(line[2])])
                        apoints_coord.append([float(line[3]), float(line[4]), float(line[5])])

        apoints_coord = np.asarray(apoints_coord)

        apoints_coord_unique, ind = np.unique(apoints_coord, axis=0, return_index=True)

        apoints_coord_unique = apoints_coord_unique[np.argsort(ind)]

        aero_params = {}
        aero_params['apoints_coord'] = apoints_coord
        aero_params['apoints_coord_unique'] = apoints_coord_unique

        return aero_params
