# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

class StaticStructureProblemParams:
    #Nastran initial geometry file
    nastran_geometry = 'nastran_input_geometry.inp'


    def __init__(self, node_id, node_id_all):

        #List of structural nodes on the outer surface
        self.node_id = node_id

        #List of all structural nodes
        self.node_id_all = node_id_all

        #Dictionary containing the structural parameters
        self.structure_params = self.get_structure_params()

        #Structural nodes coordinates (on the outer surface)
        self.node_coord = self.structure_params['node_coord']

        #Structural nodes coordinates (all nodes)
        self.node_coord_all = self.structure_params['node_coord_all']

        #Shell thicknesses
        self.t = self.structure_params['t']

        #Concentrated masses
        self.m = self.structure_params['m']


    #Function that returns the structural parameters from a Nastran input file
    def get_structure_params(self):

        node_coord = np.zeros((len(self.node_id),3))
        node_coord_all = np.zeros((len(self.node_id_all),3))
        t = []
        m = []

        #Write the outer surface node coordinates into an array
        with open(self.nastran_geometry) as f:
            lines = f.readlines()

            for line in lines:
                #Detect Nastran free field (comma separated) or small field (8 character)
                if ',' in line:
                    line = line.split(',')
                else:
                    line = [line[i:i+8] for i in range(0, len(line), 8)]

                #Remove blank spaces
                line = [word.strip() for word in line]

                if len(line) > 1:
                    if line[0] == 'GRID' and line[1] in self.node_id_all:
                        node_coord_all[self.node_id_all.index(line[1]), 0] = float(line[3])
                        node_coord_all[self.node_id_all.index(line[1]), 1] = float(line[4])
                        node_coord_all[self.node_id_all.index(line[1]), 2] = float(line[5])
                        if line[1] in self.node_id:
                            node_coord[self.node_id.index(line[1]), 0] = float(line[3])
                            node_coord[self.node_id.index(line[1]), 1] = float(line[4])
                            node_coord[self.node_id.index(line[1]), 2] = float(line[5])

                    #Write shell thicknesses into a list
                    if line [0] == 'PSHELL':
                        t.append(float(line[3]))

                    #Write concentrated masses into a list
                    if line [0] == 'CONM2':
                        m.append(float(line[4]))

        #Save thickness and mass lists as array
        t = np.asarray(t)
        m = np.asarray(m)

        structure_params = {}
        structure_params['node_coord_all'] = node_coord_all
        structure_params['node_coord'] = node_coord
        structure_params['t'] = t
        structure_params['m'] = m

        return structure_params
