# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

from openmdao.api import ExternalCodeComp

import numpy as np

import os.path

import math

import sys

from aerostructures.number_formatting.field_writer_8 import print_float_8

from aerostructures.number_formatting.is_number import isint

class NastranDynamic(ExternalCodeComp):
    template_file = 'nastran_dynamic_template.inp'

    output_file = 'nastran_dynamic.out'

    def __init__(self, node_id_all, tn, mn, M, eigr, F1, free_free=False):
        super(NastranDynamic, self).__init__()

        #Identification number of all the structural nodes
        self.node_id_all = node_id_all

        #Total number of structural nodes
        self.ns_all = len(node_id_all)

        #Number of regions where the thicknesses are defined
        self.tn = tn

        #Number of concentrated masses
        self.mn = mn

        #Number of normal modes to extract
        self.M = M

        #Normal mode extraction method
        self.eigr = eigr

        #Lower bound of the frequency range
        self.F1 = F1

        #Boolean flag indicating modal analysis with free-free conditions
        self.free_free = free_free

    def setup(self):
        #Coordinates of all structural nodes
        self.add_input('node_coord_all', val=np.zeros((self.ns_all, 3)))

        #Vector containing the thickness of each region
        self.add_input('t', val=np.zeros(self.tn))

        #Vector containing the concentrated masses' values
        self.add_input('m', val=np.zeros(self.mn))

        #Young's modulus
        self.add_input('E', val=1.)

        #Poisson's ratio
        self.add_input('nu', val=0.3)

        #Material density
        self.add_input('rho_s', val=1.)

        #Numpy array containing the N normal modes
        self.add_output('phi', val=np.zeros((3*self.ns_all, self.M)))

        #Vector containing the extracted eigenvalues
        self.add_output('eigval', val=np.zeros(self.M))

        #Vector containing the extracted generalized masses
        self.add_output('gen_mass', val=np.zeros(self.M))

        #Structural mass
        self.add_output('mass', val=1.)

        self.input_filepath = 'nastran_dynamic.inp'
        self.output_filepath = 'nastran_dynamic.pnh'

        #Check if the files exist (optional)
        self.options['external_input_files'] = [self.input_filepath,]
        #self.options['external_output_files'] = [self.output_filepath,]

        #Command according to OS
        if sys.platform == 'win32':
            self.options['command'] = ['cmd.exe', '/c', r'nastran.bat', self.input_filepath.rstrip('.inp')]
        else:
            self.options['command'] = ['nastran.cmd', self.input_filepath.rstrip('.inp')]

    def compute(self, inputs, outputs):

        # Generate the input file for Nastran from the input file template and the design variables
        self.create_input_file(inputs)

        # Parent compute function actually runs the external code
        super(NastranDynamic, self).compute(inputs, outputs)

        output_data = self.get_output_data()

        # Parse the output file from the external code and set the value of the eigenvectorss
        outputs['phi'] = output_data['phi']

        # Parse the output file from the external code and set the value of the eigenvalues
        outputs['eigval'] = output_data['eigval']

        # Parse the output file from the external code and set the value of the generalized masses
        outputs['gen_mass'] = output_data['gen_mass']

        # Parse the output file from the external code and set the value of the total mass
        outputs['mass'] = output_data['mass']


    def create_input_file(self, inputs):

        node_coord_all = inputs['node_coord_all']
        t = inputs['t']
        m = inputs['m']
        E = inputs['E']
        nu = inputs['nu']
        rho_s = inputs['rho_s']

        input_data = {}

        #Assign the mode extraction method to its input data dictionary key
        input_data['eigr'] = self.eigr

        #Assign the number of modes
        input_data['M'] = self.M

        #Assign the frequency lower bound to its input data dictionary key
        input_data['F1'] = self.F1

        #Assign each node coordinates to its corresponding node ID in the input data dictionary
        for i in range(len(node_coord_all)):
            input_data['x'+self.node_id_all[i]] = print_float_8(node_coord_all[i,0])
            input_data['y'+self.node_id_all[i]] = print_float_8(node_coord_all[i,1])
            input_data['z'+self.node_id_all[i]] = print_float_8(node_coord_all[i,2])

        #Assign each thickness value to its corresponding ID in the input data dictionary
        for i in range(len(t)):
            input_data['t'+str(i+1)] = print_float_8(t[i])

        #Assign each mass value to its corresponding ID in the input data dictionary
        for i in range(len(m)):
            input_data['m'+str(i+1)] = print_float_8(m[i])

        #Assign the Young's modulus to its input data dictionary key
        input_data['E'] = print_float_8(E)

        #Assign the Poisson's ratio to its input data dictionary key
        input_data['nu'] = print_float_8(nu)

        #Assign the material density to its input data dictionary key
        input_data['rho_s'] = print_float_8(rho_s)

        #Read the input file template
        f = open(self.template_file,'r')
        tmp = f.read()
        f.close()

        #Replace the input data contained in the dictionary onto the new input file
        new_file = tmp.format(**input_data)

        inp = open(self.input_filepath,'w')
        inp.write(new_file)
        inp.close()


    def get_output_data(self):

        #Read the punch and output files only if they exist and their last modification date is older than input file one

        while(not os.path.isfile(self.output_filepath)): pass

        while(os.path.getmtime(self.output_filepath) <= os.path.getmtime(self.input_filepath)): pass

        while(not os.path.isfile(self.output_file)): pass

        while(os.path.getmtime(self.output_file) <= os.path.getmtime(self.input_filepath)): pass

        phi = np.zeros((3*self.ns_all,self.M))

        eigval = []

        gen_mass = []

        mass = 0.

        M = self.M

        ns_all = self.ns_all

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
        with open(self.output_filepath) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for i in range(len(lines)):
                if len(lines[i]) > 1:
                    if lines[i][0] == '$EIGENVALUE':
                        total_eig_count += 1
                        #Store the eignevalue if it is a flexible mode and set flexible flag to True
                        if len(eigval) < M and total_eig_count > rigid_num:
                            eigval.append(float(lines[i][2]))
                            eig_count += 1
                            flexible = True

                        elif len(eigval) >=M:
                            flexible = False
                            break

                        else:
                            flexible = False

                    #Write eigenvectors onto phi if the node belongs to the total node list and the mode is flexible
                    elif lines[i][0] in self.node_id_all and lines[i][1] == 'G' and flexible:
                        j = self.node_id_all.index(lines[i][0])
                        phi[j][(eig_count-1)] = lines[i][2]
                        phi[j+ns_all][(eig_count-1)] = lines[i][3]
                        phi[j+2*ns_all][(eig_count-1)] = lines[i][4]

        #Normalize eigenvectors so that the maximum component equals 1
        for i in range(M):
            max_phi = phi[:,i:i+1].max()
            min_phi = phi[:,i:i+1].min()

            if abs(max_phi) > abs(min_phi):
                max_abs_phi = max_phi
            else:
                max_abs_phi = min_phi

            phi[:,i:i+1] = phi[:,i:i+1]/max_abs_phi

        #Read the Nastran output file (.out) and extract the total mass of the structure (M) and the generalized masses
        with open(self.output_file) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

        #Flag that indicates where the modal results start
        eigen = False

        for i in range(len(lines)):
            if len(lines[i]) > 5:
                if lines[i][4] == 'MASS' and lines[i][5] == 'X-C.G.':
                    mass = float(lines[i+1][1].replace('D', 'E'))

                #Set modal results flag to true
                if lines[i][0] == 'MODE' and lines[i][2] == 'EIGENVALUE':
                    eigen = True

                #Write the generalized masses into a list if their frequency is greater than 0.01 Hz (not a rigid body mode)
                if isint(lines[i][0]) and isint(lines[i][1]):
                    if eigen == True and len(gen_mass) < M and np.sqrt(abs(float(lines[i][2])))/(math.pi) > 0.01:
                        gen_mass.append(float(lines[i][5]))

                elif len(gen_mass) >=M:
                    break

        #Save the eigenvalues and generalized masses lists as numpy arrays
        eigval = np.asarray(eigval)
        gen_mass = np.asarray(gen_mass)

        output_data = {}

        output_data['phi'] = phi
        output_data['eigval'] = eigval
        output_data['gen_mass'] = gen_mass
        output_data['mass'] = mass

        return output_data
