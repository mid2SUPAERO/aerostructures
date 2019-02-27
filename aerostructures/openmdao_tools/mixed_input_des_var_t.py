# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

'''
ExplicitComponent which combines the thickness design variables with the thicknesses of the regions not defined as design variables to create a single input vector for the Nastran ExplicitComponents
'''
class MixedInputDesvarT(ExplicitComponent):


    def setup(self, tn, t_desvar_list):
        #Number of regions where the thicknesses are defined
        self.tn = tn

        #List containing the indices of the thickness vector defined as design variables
        self.t_desvar_list = t_desvar_list

        #Vector containing the baseline or default thickness of each region
        self.add_input('t_indep', val=np.zeros(self.tn))

        #Vector containing thickness design variables
        self.add_input('t_desvar', val=np.zeros(len(t_desvar_list)))

        #Vector containing the thickness of each region
        self.add_output('t', val=np.zeros(self.tn))


    def compute(self, inputs, outputs):

        t_desvar_list = self.t_desvar_list

        t_indep = inputs['t_indep']
        t_desvar = inputs['t_desvar']

        t = t_indep

        #Substitute the design variables to create the thickness and mass vectors that are the inputs of Nastran ExplicitComponents
        for i in range(len(t_desvar_list)):
            t[t_desvar_list[i]] = t_desvar[i]

        outputs['t'] = t
