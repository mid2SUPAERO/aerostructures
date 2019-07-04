# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

from openmdao.api import Component

import numpy as np

import os.path

import os

import errno

import sys

from subprocess import Popen, PIPE

import math

from aerostructures.number_formatting.is_number import isfloat, isint

class Panair(Component):
    aero_template = 'aero_template.wgs'

    current_shape = 'aero_current.wgs'

    aux_panin = 'aux_panin.aux'


    def __init__(self, na, network_info, case_name, sym_plane_index=None):
        super(Panair, self).__init__()

        #Number of aerodynamic grid points
        self.na = na

        #List containing information about each network (network ID, shape and number of points and panels of preceeding networks)
        self.network_info = network_info

        #Symmetry plane index
        self.sym_plane_index = sym_plane_index

        #Case name (for working subdirectory)
        self.case_name = case_name

        #Coordinates of the jig shape aerodynamic points (excluding the rot section points)
        self.add_param('apoints_coord', val=np.zeros((self.na, 3)))

        #Wing reference area (full aircraft configuration) (m2)
        self.add_param('Sw', val=1.)

        #Airspeed (m/s)
        self.add_param('V', val=1.)

        #Air density (kg/m3)
        self.add_param('rho_a', val=1.)

        #Displacements of the aerodynamic grid points
        self.add_param('delta', val=np.zeros((self.na, 3)))

        #Mach Number
        self.add_param('Mach', val=0.)

        #Angle of attack (alpha) (degrees)
        self.add_param('alpha', val=0.)

        #Wingspan (full aircraft configuration)
        self.add_param('b', val=1.)

        #Reference chord (c)
        self.add_param('c', 1.)

        #Forces on the aerodynamic grid points
        self.add_output('f_a', val=np.zeros((self.na, 3)))

        #Lift coefficient (full aircraft configuration)
        self.add_output('CL', val=0.)

        #Induced drag coefficient (full aircraft configuration)
        self.add_output('CDi', val=0.)

        self.input_filepath = 'a502.in'

        self.output_filepath = 'panair.out'

    def solve_nonlinear(self, params, unknowns, resids):

        case_name = self.case_name

        #Generate the wgs geometry for the current deformed shape
        self.create_current_geom(params)

        #Generate the input file for Panair from the current geometry and flow conditions
        self.create_input_file(params)

        #Clean Panair old files before running it
        os.chdir(case_name)
        #Command according to OS
        if sys.platform == 'win32':
            p = Popen('clean502.bat')
        else:
            p = Popen('clean502.sh')
        os.chdir('..')
        p.wait()

        # Run Panair
        os.chdir(case_name)
        p = Popen('panair '+self.input_filepath)
        os.chdir('..')
        p.wait()

        #Get output data from the Panair output file
        output_data = self.get_output_data()

        #Get panel pressure coefficients from output data
        pan_cp = output_data['pan_cp']

        # Parse the output file from the external code and set the value of u
        unknowns['f_a'] = self.get_forces(params, pan_cp)

        #Output lift coefficient
        unknowns['CL'] = output_data['CL']

        #Output induced drag coefficient
        unknowns['CDi'] = output_data['CDi']


    def create_current_geom(self, params):

        sym_plane_index = self.sym_plane_index

        #Compute the coordinates of the displaced points
        jig_coord = params['apoints_coord']
        new_coord = jig_coord + params['delta']

        #Enforce symmetry condition, if existing
        if sym_plane_index is not None:
            j = sym_plane_index - 1
            for i in range(len(jig_coord)):
                if jig_coord[i][j] == 0.:
                    new_coord[i][j] = 0.

        with open(self.aero_template) as f:
            lines = f.readlines()
            split_lines = [i.split() for i in lines]
            #Replace the old grid coordinates with the new ones
            #Total aerodynamic grid point counter

            j = 0
            for l in range(len(split_lines)):
                if all(isfloat(item) for item in split_lines[l]):
                    if len(split_lines[l]) == 3:
                        lines[l] = str(new_coord[j, 0])+' '+str(new_coord[j, 1])+' '+str(new_coord[j, 2])+'\n'
                        j += 1
                    if len(split_lines[l]) == 6:
                        lines[l] = str(new_coord[j, 0])+' '+str(new_coord[j, 1])+' '+str(new_coord[j, 2])+' '+str(new_coord[j+1, 0])+' '+str(new_coord[j+1, 1])+' '+str(new_coord[j+1, 2])+'\n'
                        j += 2

        case_name = self.case_name

        #Panin auxiliary file in a subdirectory for each case
        current_shape = os.path.join(os.getcwd(), case_name, self.current_shape)

        #Create subdirectory if it does not exist
        if not os.path.exists(os.path.dirname(current_shape)):
            try:
                os.makedirs(os.path.dirname(current_shape))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        #Write the new geometry file
        with open(current_shape, 'w') as f:
            for line in lines:
                f.write(line)


    #Method that creates the Panair input file from an auxiliary file by using Panin
    def create_input_file(self, params):

        case_name = self.case_name

        #Panin auxiliary file in a subdirectory for each case
        aux_panin = os.path.join(os.getcwd(), case_name, self.aux_panin)

        #Create subdirectory if it does not exist
        if not os.path.exists(os.path.dirname(aux_panin)):
            try:
                os.makedirs(os.path.dirname(aux_panin))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        #Create Panin auxiliary file with the problem inputs
        f = open(aux_panin,'w')

        #Current geometry file
        f.write('WGS '+self.current_shape+'\n')

        #Full Panair run
        f.write('CHECK 0\n')

        #Symmetric configuration
        f.write('SYMM 1\n')

        #Output 48 flow parameters
        f.write('IOUTPR 0\n')

        #Output nw force, moment, summary per net and accumulation
        f.write('IFMCPR 1\n')

        #Precision in numbers of the input file (positions after decimal point)
        f.write('PRECISION 6\n')

        #Reference chord
        f.write('CBAR '+str(params['c'])+'\n')

        #Wingspan
        f.write('SPAN '+str(params['b'])+'\n')

        #Wing reference area
        f.write('SREF '+str(params['Sw'])+'\n')

        #Mach number
        f.write('MACH '+str(params['Mach'])+'\n')

        #Compressibility angle of attack
        f.write('ALPC '+str(params['alpha'])+'\n')

        #Angle of attack
        f.write('ALPHA '+str(params['alpha'])+'\n')

        #Indirect boundary condition on an impermeable thick surface
        f.write('BOUN')
        for network in self.network_info:
            f.write(' 1')
        f.write('\n')

        #This wake condition is only valid for a single wing configuration
        #It assumes that the trailing wake is attached to the first edge of the frst network
        #Wake parallel to downstream
        #Wake length: 20 times the semispan
        f.write('WAKE 1 1 '+str(10*params['b']))

        f.close()

        #Execute Panin to generate the Panair input file
        #First, change working directory to case_name subdirectory
        os.chdir(case_name)
        #Check Python version for Popen arguments
        if (sys.version_info > (3, 0)):
            p = Popen('panin.exe', stdin=PIPE, encoding='utf8')
        else:
            p = Popen('panin.exe', stdin=PIPE)
        os.chdir('..')
        p.communicate(self.aux_panin)
        p.wait()


    def get_forces(self, params, pan_cp):

        f_a = np.zeros((self.na, 3))

        pan_cp_nw = []
        point_cf_nw = []

        #Get network information
        network_info = self.network_info

        #Create a list with the Cp results of each network
        for n in network_info:
            pan_cp_nw.append(pan_cp[n[4]:int(n[4]+(n[1]-1)*(n[2]-1))])
            point_cf_nw.append(f_a[n[3]:int(n[3]+n[1]*n[2])])

        #Compute the force coefficient for each panel on each network and distribute it over the vertices of the panel
        for n in pan_cp_nw:
            for p in n:
                #Index of the panel within a network (starting by 1)
                ip = n.index(p) + 1

                #Index of the current network
                ni = pan_cp_nw.index(n)

                #Number of rows of the network
                nm = network_info[ni][1]

                #Indices of panel vertices within a network (starting by 1)
                if ip % (nm - 1) == 0:
                    i1 = ip + ip/(nm - 1) -1
                else:
                    i1 = ip + math.floor(ip/(nm - 1))

                i2 = i1 + nm
                i3 = i1 + nm + 1
                i4 = i1 + 1

                #Indices of panel vertices within a network (starting by 0)
                i1 = int(i1 - 1)
                i2 = int(i2 - 1)
                i3 = int(i3 - 1)
                i4 = int(i4 - 1)

                #Pressure and force coefficient components of the panel
                cp = p[0]
                cfx = -cp*p[1]
                cfy = -cp*p[2]
                cfz = -cp*p[3]

                #Distribute evenly the force coefficients over the 4 vertices of the panel
                point_cf_nw[ni][i1] = point_cf_nw[ni][i1] + [cfx/4, cfy/4, cfz/4]
                point_cf_nw[ni][i2] = point_cf_nw[ni][i2] + [cfx/4, cfy/4, cfz/4]
                point_cf_nw[ni][i3] = point_cf_nw[ni][i3] + [cfx/4, cfy/4, cfz/4]
                point_cf_nw[ni][i4] = point_cf_nw[ni][i4] + [cfx/4, cfy/4, cfz/4]

        #Get the reference wing area, airspeed and density
        Sw = self.params['Sw']
        V = self.params['V']
        rho_a = self.params['rho_a']

        #Store the force coefficients components as an array and dimensionalize to obtain force values
        f_a = 0.5*rho_a*V**2*Sw*np.vstack(point_cf_nw)

        return f_a

    #Function that returns panel Cp and its unit normal vector normalized by Spanel/Sref
    def get_output_data(self):

        case_name = self.case_name
        output_filepath = os.path.join(os.getcwd(), case_name, self.output_filepath)
        input_filepath = os.path.join(os.getcwd(), case_name, self.input_filepath)

        pan_cp = []

        #Read the output file only if it exists and its last modification date is older than input file one
        while(not os.path.isfile(output_filepath)): pass

        while(os.path.getmtime(output_filepath) <= os.path.getmtime(input_filepath)): pass

        #Read the output file and store Cp and normal vector components
        with open(output_filepath) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]
            results_begin = lines.index(['0*b*solution'])
            results_end = lines.index(['full', 'configuration', 'forces', 'and', 'moments', 'summary'])

            for line in lines:
                #Get panel pressure coefficients
                if len(line) > 1 and lines.index(line) > results_begin and lines.index(line) < results_end and len(lines[lines.index(line)-1]) == 0:
                    if isint(line[0]) and isint(line[1]):
                       pan_cp.append([float(lines[lines.index(line)+1][10]), float(line[10]), float(line[11]), float(line[12])])

                #Get full configuration lift and induced drag coefficients
                if len(line) > 2:
                    if line[0] == 'full' and line[1] == 'configuration' and line[2] == 'forces':
                        i = lines.index(line)
                        CL = lines[i+11][3]
                        CDi = lines[i+11][4]

        output_data = {}

        output_data['pan_cp'] = pan_cp
        output_data['CL'] = CL
        output_data['CDi'] = CDi

        return output_data
