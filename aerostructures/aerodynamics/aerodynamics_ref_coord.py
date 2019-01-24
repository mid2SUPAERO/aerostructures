# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from aerostructures.number_formatting.is_number import isfloat

class AeroRefCoord:

    inflight_ref_shape_c = 'aero_inflight_ref_c.wgs'

    inflight_ref_shape_2 = 'aero_inflight_ref_2.wgs'

    def __init__(self):

        #Dictionary containing the aerodynamic reference coordinates
        self.aero_refs = self.get_aero_refs()

        #Coordinates of the in-flight shape of the aeroodynamic surface (reference aircraft)
        self.xa_ref_c = self.aero_refs['xa_ref_c']

        #Coordinates of the in-flight shape of the aeroodynamic surface (reference aircraft)
        self.xa_ref_2 = self.aero_refs['xa_ref_2']

    #Function that returns the aerodynamic points coordinates
    def get_aero_refs(self):

        xa_ref_c = []
        xa_ref_2 = []

        #Write the aerodynamic grid points coordinates into a list
        with open(self.inflight_ref_shape_c) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for line in lines:
                if all(isfloat(item) for item in line):
                    if len(line) == 3:
                        xa_ref_c.append([float(line[0]), float(line[1]), float(line[2])])
                    if len(line) == 6:
                        xa_ref_c.append([float(line[0]), float(line[1]), float(line[2])])
                        xa_ref_c.append([float(line[3]), float(line[4]), float(line[5])])

        #Write the aerodynamic grid points coordinates into a list (excluding the root section)
        with open(self.inflight_ref_shape_2) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for line in lines:
                if all(isfloat(item) for item in line):
                    if len(line) == 3:
                        xa_ref_2.append([float(line[0]), float(line[1]), float(line[2])])
                    if len(line) == 6:
                        xa_ref_2.append([float(line[0]), float(line[1]), float(line[2])])
                        xa_ref_2.append([float(line[3]), float(line[4]), float(line[5])])

        xa_ref_c = np.asarray(xa_ref_c)
        xa_ref_2 = np.asarray(xa_ref_2)

        aero_refs = {}
        aero_refs['xa_ref_c'] = xa_ref_c
        aero_refs['xa_ref_2'] = xa_ref_2

        return aero_refs
