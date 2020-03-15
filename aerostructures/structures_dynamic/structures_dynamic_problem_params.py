# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

class DynamicStructureProblemParams:
    #Nastran initial geometry file
    nastran_geometry = 'nastran_input_geometry.inp'

    #Reference modal results file
    nastran_modal_ref = 'nastran_dynamic_ref'


    def __init__(self, node_id_all, N, free_free=False):

        #List of all structural nodes
        self.node_id_all = node_id_all

        #Total number of structural nodes
        self.ns_all = len(node_id_all)

        #Number of normal modes to consider for the comparison
        self.N = N

        #Boolean flag indicating modal analysis with free-free conditions
        self.free_free = free_free

        #Dictionary containing the structural parameters
        self.structure_params = self.get_structure_params()

        #Dictionary containing reference modal data
        self.modal_ref = self.get_modal_ref()

        #Structural nodes coordinates (all nodes)
        self.node_coord_all = self.structure_params['node_coord_all']

        #Shell thicknesses
        self.t = self.structure_params['t']

        #Concentrated masses
        self.m = self.structure_params['m']

        #Reference normal modes
        self.phi_ref = self.modal_ref['phi_ref']

        #Reference eigenvalues
        self.eigval_ref = self.modal_ref['eigval_ref']

        #Reference mass
        self.mass_ref = self.modal_ref['mass_ref']


    #Function that returns the structural parameters from a Nastran input file
    def get_structure_params(self):

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

                    #Write shell thicknesses into a list
                    if line [0] == 'PSHELL':
                        t.append(float(line[3]))

                    #Write concentrated masses into a list
                    if line [0] == 'CONM2':
                        m.append(float(line[4]))

        #Save thickness and mass lists as arrays
        t = np.asarray(t)
        m = np.asarray(m)

        structure_params = {}
        structure_params['node_coord_all'] = node_coord_all
        structure_params['t'] = t
        structure_params['m'] = m

        return structure_params

    def get_modal_ref(self):

        N = self.N
        ns_all = self.ns_all

        phi_ref = np.zeros((3*self.ns_all,N))
        eigval_ref = []
        mass_ref = 0.

        free_free = self.free_free

        #Number of rigid modes (offset) according to the free-free condition
        if free_free:
            rigid_num = 6
        else: rigid_num = 0

        #Total normal mode counter (including rigid ones)
        total_eig_count = 0

        #Normal mode counter (elastic)
        eig_count = 0

        #Boolean that indicates whether a mode is flexible or not
        flexible = False

        #Read the Nastran punch file (.pnh) and extract eigenvalues and eigenvectors
        with open(self.nastran_modal_ref + '.pnh') as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for i in range(len(lines)):
                if len(lines[i]) > 1:
                    if lines[i][0] == '$EIGENVALUE':
                        total_eig_count += 1
                        #Store the eignevalue if it is a flexible mode and set flexible flag to True
                        if len(eigval_ref) < N and total_eig_count > rigid_num:
                            eigval_ref.append(float(lines[i][2]))
                            eig_count += 1
                            flexible = True

                        elif len(eigval_ref) >=N:
                            flexible = False
                            break

                        else:
                            flexible = False

                    #Write eigenvectors onto phi_ref if the node belongs to the total node list and the mode is flexible
                    elif lines[i][0] in self.node_id_all and lines[i][1] == 'G' and flexible:
                        j = self.node_id_all.index(lines[i][0])
                        phi_ref[j][(eig_count-1)] = lines[i][2]
                        phi_ref[j+ns_all][(eig_count-1)] = lines[i][3]
                        phi_ref[j+2*ns_all][(eig_count-1)] = lines[i][4]

        #Normalize eigenvectors so that the maximum component equals 1
        for i in range(N):
            max_phi_ref = phi_ref[:,i:i+1].max()
            min_phi_ref = phi_ref[:,i:i+1].min()

            if abs(max_phi_ref) > abs(min_phi_ref):
                max_abs_phi_ref = max_phi_ref
            else:
                max_abs_phi_ref = min_phi_ref

            phi_ref[:,i:i+1] = phi_ref[:,i:i+1]/max_abs_phi_ref

        #Read the Nastran output file (.out) and extract the total reference mass of the structure
        with open(self.nastran_modal_ref + '.out') as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

        for i in range(len(lines)):
            if len(lines[i]) > 5:
                if lines[i][4] == 'MASS' and lines[i][5] == 'X-C.G.':
                    mass_ref = float(lines[i+1][1].replace('D', 'E'))

        #Save the eigenvalues list as a numpy array
        eigval_ref = np.asarray(eigval_ref)

        modal_ref = {}

        modal_ref['phi_ref'] = phi_ref
        modal_ref['eigval_ref'] = eigval_ref
        modal_ref['mass_ref'] = mass_ref

        return modal_ref
