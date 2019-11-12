# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

from openmdao.api import Component

import numpy as np

from baseclasses import *

from adflow import ADFLOW

import pywarpustruct

class ADflow(Component):

    def __init__(self, na, aeroOptions, sym_plane_index=None):
        super(ADflow, self).__init__()

        #Number of aerodynamic surface grid points
        self.na = na
        
        #Symmetry plane index
        self.sym_plane_index = sym_plane_index

		#Surface points coordinates (jig shape)
        self.add_param('jig_surface_coord', val=np.zeros((na,3)))
        
        #Wing reference area (full aircraft configuration)
        self.add_param('Sw', val=1.)
        
        #Flight altitude (meters)
        self.add_param('h', val=0.)
        
        #Displacements of the aerodynamic surface grid points
        self.add_param('delta', val=np.zeros((na,3)))
        
        #Mach Number
        self.add_param('Mach', val=0.)
        
        #Angle of attack (alpha) (degrees)
        self.add_param('alpha', val=0.)
        
        #Wing reference chord
        self.add_param('c', val=1.)

        #Forces on the aerodynamic surface grid points
        self.add_output('f_a', val=np.zeros((na,3)))

        #Lift coefficient
        self.add_output('CL', val=0.)

        #Drag coefficient
        self.add_output('CD', val=0.)

        self.name = 'fc'
        
        self.aeroOptions = aeroOptions

        mesh = pywarpustruct.USMesh(options=self.aeroOptions)

        # Create solver
        self.CFDSolver = ADFLOW(options=self.aeroOptions)
        self.CFDSolver.setMesh(mesh)


    def solve_nonlinear(self, params, unknowns, resids):
		
		jig_surface_coord = params['jig_surface_coord']
		
		Sw = params['Sw']
		
		h = params['h']
		
		delta = params['delta']
		
		Mach = params['Mach']
		
		alpha = params['alpha']
		
		c = params['c']
		
		sym_plane_index = self.sym_plane_index

		#Add surface displacements to jig shape
		aero_surf_coord = jig_surface_coord + delta
		
		#Enforce symmetry condition, if existing
		if sym_plane_index is not None:
			j = sym_plane_index - 1
			for i in range(len(jig_surface_coord)):
				if jig_surface_coord[i][j] == 0.:
					aero_surf_coord[i][j] = 0.
			#Use half-surface as the reference surface if symmetry exists
			Sw = Sw/2.

		self.CFDSolver.setSurfaceCoordinates(aero_surf_coord)

		# Aerodynamic problem description
		ap = AeroProblem(name=self.name, alpha=alpha, mach=Mach, altitude=h,
						 areaRef=Sw, chordRef=c, evalFuncs=['cl','cd'])

		# Solve and evaluate functions
		funcs = {}
		self.CFDSolver(ap)
		self.CFDSolver.evalFunctions(ap, funcs)

		# Set the value of the unkowns
		unknowns['f_a'] = self.CFDSolver.getForces()

		unknowns['CL'] = funcs[self.name + '_cl']

		unknowns['CD'] = funcs[self.name + '_cd']
