# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which combines the thickness design variables with the thicknesses of the regions not defined as design variables to create a single input vector for the Nastran components
'''
class MixedInputDesvarT(Component):


    def __init__(self, tn, t_desvar_list):
        super(MixedInputDesvarT, self).__init__()

        #Number of regions where the thicknesses are defined
        self.tn = tn

        #List containing the indices of the thickness vector defined as design variables
        self.t_desvar_list = t_desvar_list

        #Vector containing the baseline or default thickness of each region
        self.add_param('t_indep', val=np.zeros(self.tn))

        #Vector containing thickness design variables
        self.add_param('t_desvar', val=np.zeros(len(t_desvar_list)))

        #Vector containing the thickness of each region
        self.add_output('t', val=np.zeros(self.tn))


    def solve_nonlinear(self, params, unknowns, resids):

        t_desvar_list = self.t_desvar_list

        t_indep = params['t_indep']
        t_desvar = params['t_desvar']

        t = t_indep

        #Substitute the design variables to create the thickness and mass vectors that are the inputs of Nastran components
        for i in range(len(t_desvar_list)):
            t[t_desvar_list[i]] = t_desvar[i]

        unknowns['t'] = t
