# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from aerostructures.number_formatting.is_number import isfloat, isint

class AeroProblemDimensions:
    #Jig shape geometry
    aero_template = 'aero_template.wgs'


    def __init__(self):
        #Dictionary containing the aerodynamic problem dimensions
        self.aero_dimensions = self.get_aero_dimensions()

        #Number of aerodynamic grid points
        self.na = self.aero_dimensions['na']

        #Number of unique aerodynamic grid points
        self.na_unique = self.aero_dimensions['na_unique']

        #Aerodynamic mesh network information list
        self.network_info = self.aero_dimensions['network_info']


    def get_aero_dimensions(self):

        apoints_coord = []
        network_info = []

        #Write the aerodynamic grid points coordinates into a list
        with open(self.aero_template) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            points = 0
            pans = 0

            for line in lines:
                #Get aerodynamic grid points coordinates
                if all(isfloat(item) for item in line):
                    if len(line) == 3:
                        apoints_coord.append([float(line[0]), float(line[1]), float(line[2])])
                    if len(line) == 6:
                        apoints_coord.append([float(line[0]), float(line[1]), float(line[2])])
                        apoints_coord.append([float(line[3]), float(line[4]), float(line[5])])

                #Get network information
                if len(line) > 1:
                    if isint(line[0]):
                        network_info.append([int(line[0]), int(line[2]), int(line[1]), int(points), int(pans)])
                        points = points + int(line[2])*int(line[1])
                        pans = pans + (int(line[2]) - 1)*(int(line[1]) - 1)

        apoints_coord = np.asarray(apoints_coord)
        na = len(apoints_coord)

        apoints_coord_unique = np.unique(apoints_coord, axis=0)
        na_unique = len(apoints_coord_unique)

        #Dictionary containing aerodynamic problem data
        aero_dimensions = {}
        aero_dimensions['na'] = na
        aero_dimensions['na_unique'] = na_unique
        aero_dimensions['network_info'] = network_info

        return aero_dimensions
