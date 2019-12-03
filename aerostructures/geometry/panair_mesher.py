# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import sys

import math

import numpy as np

from openmdao.api import ExternalCode

class PanairMesher(ExternalCode):
    geo_script = 'aero_jig.geo'

    jig_mesh = 'aero_jig.msh'


    def __init__(self, n_sec, na, na_unique, network_info, ref_airfoil_files):
        super(PanairMesher, self).__init__()

        #Number of sections for the geometry definition
        self.n_sec = n_sec

        #Number of aerodynamic grid points
        self.na = na

        #Number of unique aerodynamic_grid_points
        self.na_unique = na_unique

        #List containing information about each network (network ID, shape and number of points and panels of preceeding networks)
        self.network_info = network_info

        #Filenames of the reference airfoil files
        self.ref_airfoil_files = ref_airfoil_files

        #Coordinates x,y,z of the leading edge for all sections
        self.add_param('x_le', val=np.zeros(n_sec))
        self.add_param('y_le', val=np.zeros(n_sec))
        self.add_param('z_le', val=np.zeros(n_sec))

        #Geometric twist for all sections
        self.add_param('theta', val=np.zeros(n_sec))

        #Thickness-to-chord ratio for all sections
        self.add_param('tc', val=np.zeros(n_sec))

        #Maximum camber-to-chord ratio for all sections
        self.add_param('camc', val=np.zeros(n_sec))

        #Chord length for all sections
        self.add_param('chords', val=np.zeros(n_sec))

        #Coordinates of the jig shape aerodynamic points
        self.add_output('apoints_coord', val=np.zeros((self.na, 3)))

        #Coordinates of the unique jig shape aerodynamic points
        self.add_output('apoints_coord_unique', val=np.zeros((self.na_unique, 3)))

        self.input_filepath = self.geo_script

        self.output_filepath = self.jig_mesh

        #Check if the files exist (optional)
        self.options['external_input_files'] = [self.input_filepath]
        #self.options['external_output_files'] = [self.output_filepath]

        #Command according to OS
        if sys.platform == 'win32':
            self.options['command'] = ['cmd.exe', '/c', r'gmsh.exe', self.input_filepath, r'-2', r'-o', self.output_filepath]
        else:
            self.options['command'] = ['panair', self.input_filepath]

    def solve_nonlinear(self, params, unknowns, resids):

        #Get the coordinates, tc, and camc of the reference airfoil file
        ref_airfoils = self.read_reference_airfoils()

        #Generate the gmsh script defining the geometry
        self.create_gmsh_script(params, ref_airfoils)

        # Parent solve_nonlinear function actually runs the external code
        super(PanairMesher, self).solve_nonlinear(params, unknowns, resids)

        #Get output data from the Panair output file
        aero_points = self.get_aero_points()

        #Output jig shape aerodynamic mesh coordinates
        unknowns['apoints_coord'] = aero_points['apoints_coord']

        #Output unique jig shape aerodynamic mesh coordinates
        unknowns['apoints_coord_unique'] = aero_points['apoints_coord_unique']


    def read_reference_airfoils(self):

        ref_airfoil_files = self.ref_airfoil_files
        ref_airfoils = {}

        for ref_airfoil_file in set(ref_airfoil_files):
            #Coordinates of the reference airfoil's upper surface
            upper_coord = []

            #Coordinates of the reference airfoil's lower surface
            lower_coord = []

            with open(ref_airfoil_file) as f:
                lines = f.readlines()
                lines = [i.split() for i in lines]

                coord = False
                for line in lines:
                    if len (line) == 4:
                        if line[0] == 'XU': coord = True
                    if coord == True and len (line) == 4 and line[0] != 'XU':
                        upper_coord.append((float(line[0]), float(line[1])))
                        lower_coord.append((float(line[2]), float(line[3])))

            #Compute tc and camc of the reference airfoil
            #First, compute thickness and camber along the chord
            t_ref = [upper_coord[i][1] - lower_coord[i][1] for i in range(len(upper_coord))]
            camber_ref = [(upper_coord[i][1] + lower_coord[i][1])/2 for i in range(len(upper_coord))]

            #Convert to numpy array
            t_ref = np.asarray(t_ref)
            camber_ref = np.asarray(camber_ref)

            #Compute chord of the reference airfoil
            c_ref = upper_coord[-1][0] - upper_coord[0][0]

            #Compute t/c and camber/c for the reference airfoil
            tc_ref = t_ref.max()/c_ref
            camc_ref = camber_ref.max()/c_ref
            #Modified by JMC 15/08/2018: In case of symmetrical airfoil, set camc_ref to arbitrary value to avoid dividing by zero
            if camc_ref == 0.: camc_ref = 1.

            #Convert reference airfoil coordinates to numpy array and normalize using reference chord
            upper_coord = np.asarray(upper_coord)/c_ref
            lower_coord = np.asarray(lower_coord)/c_ref

            ref_airfoil = {}

            ref_airfoil['upper_coord'] = upper_coord
            ref_airfoil['lower_coord'] = lower_coord
            ref_airfoil['t_ref'] = t_ref
            ref_airfoil['camber_ref'] = camber_ref
            ref_airfoil['tc_ref'] = tc_ref
            ref_airfoil['camc_ref'] = camc_ref

            ref_airfoils[ref_airfoil_file] = ref_airfoil
        
        return ref_airfoils

    def create_gmsh_script(self, params, ref_airfoils):

        geo_script = self.geo_script
        network_info = self.network_info
        ref_airfoil_files = self.ref_airfoil_files

        xle = params['x_le']
        yle = params['y_le']
        zle = params['z_le']
        theta = params['theta']
        c = params['chords']
        tc = params['tc']
        camc = params['camc']

        #Override twist of the root section and set it to zero to avoid conflict with AoA
        theta[0] = 0.
        
        #Define section number
        sec_num = self.n_sec

        #Define cols and rows from network_info and sec_num
        rows = network_info[0][1] - 1
        cols = (network_info[0][2] - 1)//(sec_num - 1)

        self.rows = rows
        self.cols = cols

        #Tolerance for nonzero line length
        delta = 1.e-6

        with open(geo_script,'w') as f:
            for i in range(sec_num):

                tc_ref = ref_airfoils[ref_airfoil_files[i]]['tc_ref']
                camc_ref = ref_airfoils[ref_airfoil_files[i]]['camc_ref']
                upper_coord = ref_airfoils[ref_airfoil_files[i]]['upper_coord']
                lower_coord = ref_airfoils[ref_airfoil_files[i]]['lower_coord']
                half_thick_ref = ref_airfoils[ref_airfoil_files[i]]['t_ref']/2
                camber_ref = ref_airfoils[ref_airfoil_files[i]]['camber_ref']

                #Define number of points along the airfoil
                foil_num = len(upper_coord)

                #Write upper surface coordinates
                for j in range(foil_num):
                    if (j == 0 or j == foil_num - 1):
                        y_u = camc[i]/camc_ref*camber_ref[j] + tc[i]/tc_ref*half_thick_ref[j]
                        f.write('Point('+str(j+1+2*i*len(upper_coord))+') = {'+str(c[i]*float(upper_coord[j][0]))+', '+str(-(i+1))+', '+str(c[i]*y_u+delta)+'};\n')
                    else:
                        y_u = camc[i]/camc_ref*camber_ref[j] + tc[i]/tc_ref*half_thick_ref[j]
                        f.write('Point('+str(j+1+2*i*len(upper_coord))+') = {'+str(c[i]*float(upper_coord[j][0]))+', '+str(-(i+1))+', '+str(c[i]*y_u)+'};\n')

                #Write lower surface coordinates
                offset = len(upper_coord)
                for j in range(foil_num):
                    y_l = camc[i]/camc_ref*camber_ref[j] - tc[i]/tc_ref*half_thick_ref[j]
                    f.write('Point('+str(j+1+offset+2*i*len(lower_coord))+') = {'+str(c[i]*float(lower_coord[j][0]))+', '+str(-(i+1))+', '+str(c[i]*y_l)+'};\n')

                #Create upper surface spline
                f.write('Spline('+str(2*i+1)+') = {'+str(1+2*i*len(upper_coord))+':'+str((2*i+1)*len(upper_coord))+'};\n')

                #Create lower surface spline
                f.write('Spline('+str(2*i+2)+') = {'+str(len(upper_coord)+1+2*i*len(upper_coord))+':'+str(2*(i+1)*len(upper_coord))+'};\n\n')

        #Translation of the airfoil sections
            for i in range(sec_num):
                f.write('Translate {'+str(xle[i])+', '+str(yle[i]+i+1)+', '+str(zle[i])+'} {Duplicata{Line{'+str(2*i+1)+', '+str(2*i+2)+'};}}\n\n')

        #Rotation of the airfoil sections
            for i in range(sec_num):
                f.write('Rotate {{0, 1, 0}, {'+str(xle[i])+', '+str(yle[i])+', '+str(zle[i])+'}, '+str(math.radians(theta[i]))+'} {Line{'+str(2*i+1+2*sec_num)+', '+str(2*i+2+2*sec_num)+'};}\n\n')

        #Create trailing edge lines (upper surface)
            for i in range(1, sec_num):
                f.write('Line('+str(4*sec_num+i)+') = {'+str(2*foil_num*sec_num+(i-1)*2*(foil_num+1)+foil_num)+', '+str(2*foil_num*sec_num+i*2*(foil_num+1)+foil_num)+'};\n')
            f.write('\n')

        #Create leading edge lines (upper surface)
            for i in range(1, sec_num):
                f.write('Line('+str(5*sec_num+i-1)+') = {'+str(2*foil_num*sec_num+(2*(i-1)*(foil_num+1)+1))+', '+str(2*foil_num*sec_num+2*i*(foil_num+1)+1)+'};\n')
            f.write('\n')

        #Create trailing edge lines (lower surface)
            for i in range(1, sec_num):
                f.write('Line('+str(4*sec_num+2*(sec_num-1)+i)+') = {'+str(2*foil_num*sec_num+i*2*(foil_num+1))+', '+str(2*foil_num*sec_num+(i+1)*2*(foil_num+1))+'};\n')
            f.write('\n')

        #Create leading edge lines (lower surface)
            for i in range(1, sec_num):
                f.write('Line('+str(4*sec_num+3*(sec_num-1)+i)+') = {'+str(2*foil_num*sec_num+(i-1)*2*(foil_num+1)+foil_num+3)+', '+str(2*foil_num*sec_num+i*2*(foil_num+1)+foil_num+3)+'};\n')
            f.write('\n')

        #Create trailing and leading edge wingtip lines
            f.write('Line('+str(4*sec_num+3*(sec_num-1)+i+1)+') = {'+str(2*foil_num*sec_num+i*2*(foil_num+1)+foil_num)+', '+str(2*foil_num*sec_num+(i+1)*2*(foil_num+1))+'};\n')
            f.write('Line('+str(4*sec_num+3*(sec_num-1)+i+2)+') = {'+str(2*foil_num*sec_num+i*2*(foil_num+1)+foil_num+3)+', '+str(2*foil_num*sec_num+2*i*(foil_num+1)+1)+'};\n')

        #Transform trailing edges into transfinite lines (upper surface)
            for i in range(1, sec_num):
                f.write('Transfinite Line {'+str(4*sec_num+i)+'} = ('+str(cols+1)+') Using Progression 1;\n')

        #Transform leading edges into transfinite lines (upper surface)
            for i in range(1, sec_num):
                f.write('Transfinite Line {'+str(5*sec_num+i-1)+'} = ('+str(cols+1)+') Using Progression 1;\n')
            f.write('\n')

        #Transform trailing edges into transfinite lines (upper surface)
            for i in range(1, sec_num):
                f.write('Transfinite Line {'+str(4*sec_num+2*(sec_num-1)+i)+'} = ('+str(cols+1)+') Using Progression 1;\n')

        #Transform leading edges into transfinite lines (upper surface)
            for i in range(1, sec_num):
                f.write('Transfinite Line {'+str(4*sec_num+3*(sec_num-1)+i)+'} = ('+str(cols+1)+') Using Progression 1;\n')
            f.write('\n')

        #Transform wingtip lines into transfinite lines
            f.write('Transfinite Line {'+str(4*sec_num+3*(sec_num-1)+i+1)+'} = (3) Using Progression 1;\n')
            f.write('Transfinite Line {'+str(4*sec_num+3*(sec_num-1)+i+2)+'} = (3) Using Progression 1;\n')

        #Compute GMSH bump corresponding to a cosine spacing rule
            bump = (1-math.cos(math.pi/rows))/(2*math.sin(math.pi/(2*rows)))

        #Transform airfoil splines into transfinite lines
            for i in range(2*sec_num):
                f.write('Transfinite Line {'+str(2*sec_num+i+1)+'} = ('+str(rows+1)+') Using Bump '+str(bump)+';\n')
            f.write('\n')

        #Create upper surface line loops
            for i in range(1, sec_num):
                f.write('Line Loop('+str(i)+') = {'+str(4*sec_num+i)+', '+str(-(2*sec_num+2*i+1))+', '+str(-(4*sec_num+i+sec_num-1))+', '+str(2*sec_num+2*i-1)+'};\n')
            f.write('\n')

        #Create lower surface line loops
            for i in range(1, sec_num):
                f.write('Line Loop('+str(i+sec_num-1)+') = {'+str(4*sec_num+i+3*(sec_num-1))+', '+str(2*sec_num+2*(i+1))+', '+str(-(4*sec_num+i+2*(sec_num-1)))+', '+str(-(2*sec_num+2*i))+'};\n')
            f.write('\n')

        #Create wingtip surface line loop
            f.write('Line Loop('+str(i+sec_num)+') = {'+str((4*sec_num+3*(sec_num-1)+i+1))+', '+str(-(2*sec_num+2*(i+1)))+', '+str((4*sec_num+3*(sec_num-1)+i+2))+', '+str((2*sec_num+2*i+1))+'};\n')
            f.write('\n')

        #Create surfaces
            for i in range(1, 2*sec_num):
                f.write('Ruled Surface('+str(i)+') = {'+str(i)+'};\n')
                f.write('Transfinite Surface {'+str(i)+'};\n')
                f.write('Recombine Surface {'+str(i)+'};\n\n')

        #Create 2D mesh
            f.write('Mesh 2;\n\n')

        #Create physical surface from all surfaces
            f.write('Physical Surface(1) = {1:'+str(2*(sec_num-1)+1)+'};')


    def get_aero_points(self):

        jig_mesh = self.jig_mesh
        sec_num = self.n_sec
        rows = self.rows
        cols = self.cols

        nodes = {}

        elm_list = []

        elm_dict = {}

        with open(jig_mesh) as f:
            lines = f.readlines()
            nodes_beg = lines.index('$Nodes\n')
            nodes_end = lines.index('$EndNodes\n')
            elms_beg = lines.index('$Elements\n')
            elms_end = lines.index('$EndElements\n')
            lines = [i.split() for i in lines]

        for i in range (len(lines)):
            if i > (nodes_beg+1) and i < nodes_end:
                nodes[int(lines[i][0])] = [float(lines[i][1]), float(lines[i][2]), float(lines[i][3])]

            if i > (elms_beg+1) and i < elms_end:
                elm_list.append(int(lines[i][0]))
                elm_dict[int(lines[i][0])] = [int(lines[i][5]), int(lines[i][6]), int(lines[i][7]), int(lines[i][8])]

        #Redefine number of columns of the whole wing
        cols = (sec_num - 1)*cols

        #Table containing the elements of the upper network
        elm_net_upper = np.zeros((rows, cols), dtype=np.dtype(int))

        #Table containing the elements of the lower network
        elm_net_lower = np.zeros((rows, cols), dtype=np.dtype(int))

        #Table containing the elements of the wingtip surface
        elm_net_tip = np.zeros((rows, 2), dtype=np.dtype(int))

        for i in range(rows):
            for j in range(cols):
                elm_net_upper[i][j] = elm_list[j*rows+i]
                elm_net_lower[i][j] = elm_list[j*rows+i+rows*cols]

            for j in range(2):
                elm_net_tip[i][j] = elm_list[j*rows+i+2*rows*cols]

        #Table containing the nodes of the upper network
        nodes_net_upper = np.zeros((rows+1, cols+1))

        #Table containing the nodes of the lower network
        nodes_net_lower = np.zeros((rows+1, cols+1))

        #Table containing the nodes of wing tip
        nodes_net_tip = np.zeros((rows+1, 3))

        for i in range(rows):
            for j in range(cols):
                elm_upper = elm_net_upper[i][j]
                nodes_net_upper[i][j] = elm_dict[elm_upper][0]
                nodes_net_upper[i][j+1] = elm_dict[elm_upper][1]
                nodes_net_upper[i+1][j+1] = elm_dict[elm_upper][2]
                nodes_net_upper[i+1][j] = elm_dict[elm_upper][3]

                elm_lower = elm_net_lower[i][j]
                nodes_net_lower[i][j] = elm_dict[elm_lower][0]
                nodes_net_lower[i][j+1] = elm_dict[elm_lower][1]
                nodes_net_lower[i+1][j+1] = elm_dict[elm_lower][2]
                nodes_net_lower[i+1][j] = elm_dict[elm_lower][3]

            for j in range(2):
                elm_tip = elm_net_tip[i][j]
                nodes_net_tip[i][j] = elm_dict[elm_tip][0]
                nodes_net_tip[i][j+1] = elm_dict[elm_tip][1]
                nodes_net_tip[i+1][j+1] = elm_dict[elm_tip][2]
                nodes_net_tip[i+1][j] = elm_dict[elm_tip][3]

        #Remove gap between upper and lower surfaces at the trailing and leading edges
        for j in range(cols+1):
            for i in range(3):
                nodes[nodes_net_upper[0][j]][i] = nodes[nodes_net_lower[rows][j]][i]
                nodes[nodes_net_upper[rows][j]][i] = nodes[nodes_net_lower[0][j]][i]

        for j in range(2):
            for i in range(3):
                nodes[nodes_net_tip[0][j]][i] = nodes[nodes_net_tip[0][-1]][i]
                nodes[nodes_net_tip[-1][j]][i] = nodes[nodes_net_tip[-1][-1]][i]

        apoints_coord = []

        for j in range(cols+1):
            for i in range(rows+1):
                apoints_coord.append(nodes[nodes_net_upper[i][j]])

        for j in range(cols+1):
            for i in range(rows+1):
                apoints_coord.append(nodes[nodes_net_lower[i][j]])

        for j in range(3):
            for i in range(rows+1):
                apoints_coord.append(nodes[nodes_net_tip[i][j]])

        #Store as numpy array
        apoints_coord = np.asarray(apoints_coord)

        apoints_coord_unique, ind = np.unique(apoints_coord, axis=0, return_index=True)

        apoints_coord_unique = apoints_coord_unique[np.argsort(ind)]

        aero_points = {}
        aero_points['apoints_coord'] = apoints_coord
        aero_points['apoints_coord_unique'] = apoints_coord_unique

        return aero_points
