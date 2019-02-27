# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

'''
ExplicitComponent which combines the thickness and mass design variables with the thicknesses and masses not defined as design variables to create a single input vector for the Nastran ExplicitComponents
'''
class MixedInputDesvar(ExplicitComponent):

    def __init__(self, tn, mn, t_desvar_list=[], m_desvar_list=[]):
        super(MixedInputDesvar, self).__init__()

        #Number of regions where the thicknesses are defined
        self.tn = tn

        #Number of concentrated masses
        self.mn = mn

        #List containing the indices of the thickness vector defined as design variables
        self.t_desvar_list = t_desvar_list

        #List containing the indices of the thickness vector defined as design variables
        self.m_desvar_list = m_desvar_list

    def setup(self):
        #Vector containing the baseline or default thickness of each region
        self.add_input('t_indep', val=np.zeros(self.tn))

        #Vector containing the baseline or default concentrated masses' values
        self.add_input('m_indep', val=np.zeros(self.mn))

        #Vector containing thickness design variables
        self.add_input('t_desvar', val=np.zeros(len(self.t_desvar_list)))

        #Vector containing concentrated masses design variables
        self.add_input('m_desvar', val=np.zeros(len(self.m_desvar_list)))

        #Vector containing the thickness of each region
        self.add_output('t', val=np.zeros(self.tn))

        #Vector containing the concentrated masses' values
        self.add_output('m', val=np.zeros(self.mn))


    def compute(self, inputs, outputs):

        t_desvar_list = self.t_desvar_list
        m_desvar_list = self.m_desvar_list

        t_indep = inputs['t_indep']
        m_indep = inputs['m_indep']
        t_desvar = inputs['t_desvar']
        m_desvar = inputs['m_desvar']

        t = t_indep
        m = m_indep

        #Substitute the design variables to create the thickness and mass vectors that are the inputs of Nastran ExplicitComponents
        for i in range(len(t_desvar_list)):
            t[t_desvar_list[i]] = t_desvar[i]

        for i in range(len(m_desvar_list)):
            m[m_desvar_list[i]] = m_desvar[i]

        outputs['t'] = t
        outputs['m'] = m
