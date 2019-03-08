# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

from openmdao.api import ExternalCode

import numpy as np

import os, glob, time

import re

import math

from aerostructures import isint, isfloat, print_float_8

class Flutter(ExternalCode):
    template_file = 'flutter_input_template.bdf'
    
    output_file = 'nastran_flutter.f06'
    
    
    def __init__(self, N, F, n_sec):
        super(Flutter, self).__init__()
        
        #Number of normal modes
        self.N = N
        
        #Number of reduced frequencies to consider
        self.F = F
        
        #Number of sections of the aerodynamic surface (not segments)
        self.n_sec = n_sec
        
        #Vector of section chords
        self.add_param('c', val=np.zeros(n_sec))
        
        #Vector of section leading edge positions
        self.add_param('x_le', val=np.zeros(n_sec))
        
        #Numpy array containing the real part of the F N by N aerodynamic coefficient matrices        
        self.add_output('Qr', val=np.zeros((N, F*N)))
        
        #Numpy array containing the imaginary part of the F N by N aerodynamic coefficient matrices        
        self.add_output('Qi', val=np.zeros((N, F*N)))
        
        self.input_filepath = 'nastran_flutter.bdf'
        self.output_filepath = 'nastran_flutter.f06'
        
        #Check if the files exist (optional)        
        self.options['external_input_files'] = [self.input_filepath,]
        #self.options['external_output_files'] = [self.output_filepath,]
        
        self.options['command'] = ['cmd.exe', '/c', r'nastran.exe', self.input_filepath]
        
        
    def solve_nonlinear(self, params, unknowns, resids):
        
        # Generate the input file for Nastran from the input file template and the design variables
        self.create_input_file(params)
        
        # Parent solve_nonlinear function actually runs the external code
        super(Flutter, self).solve_nonlinear(params, unknowns, resids)
        
        output_data = self.get_output_data()
        
        # Parse the output file from the external code and set the real part of the aerodynamic matrices
        unknowns['Qr'] = output_data['Qr']
        
        # Parse the output file from the external code and set the imaginary part of the aerodynamic matrices
        unknowns['Qi'] = output_data['Qi']
        
        
    def create_input_file(self, params):
        
        #Clean up old input and output files
        for filename in glob.glob(self.input_filepath.rstrip('bdf')+"*"):
            os.remove(filename)
        
        n_sec = self.n_sec
        
        c = params['c']
        x_le = params['x_le']
        
        input_data = {}
        
        #Assign the chords and leading edge positions to their input data dictionary key
        for i in range(n_sec):
            input_data['c'+str(i+1)] = print_float_8(c[i])
            input_data['x_le'+str(i+1)] = print_float_8(x_le[i])
                
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
        
        #Read the output file only if it exists and its last modification date is older than input file one
        
        while(not os.path.isfile(self.output_filepath)): pass
        
        while(os.path.getmtime(self.output_filepath) <= os.path.getmtime(self.input_filepath)): pass
    
        N = self.N
        
        F = self.F
        
        #Read the Nastran output file (.f06) and extract aerodynamic matrices QHHL   
        # Read in the file    
        with open(self.output_filepath, 'r') as f:
            lines = f.readlines()
            lines = [re.sub("[^\w).+-]", " ",  i).split() for i in lines]
            
        real = []
        img = []
            
        for line in lines:
            if len(line) > 0:
                if line[0] == '1)' or line[0] == '6)':
                    #Real or imaginary flag
                    real_flag = True
                    for item in line:
                        if real_flag and isfloat(item):
                            real.append(item)
                            real_flag = False
                            
                        elif not real_flag and isfloat(item):
                            img.append(item)
                            real_flag = True
        
        real = np.transpose(np.reshape(real, (F*N, N)))
        img = np.transpose(np.reshape(img, (F*N, N)))
                        
        output_data = {}                
        
        output_data['Qr'] = real
        output_data['Qi'] = img
        
        return output_data