# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

'''
Component which combines the mass design variables with the masses of the points not defined as design variables to create a single input vector for the Nastran components
'''
class MixedInputDesvarM(Component):


    def __init__(self, mn, m_desvar_list=[]):
        super(MixedInputDesvarM, self).__init__()

        #Number of concentrated masses
        self.mn = mn

        #List containing the indices of the thickness vector defined as design variables
        self.m_desvar_list = m_desvar_list

        #Vector containing the baseline or default concentrated masses' values
        self.add_param('m_indep', val=np.zeros(self.mn))

        #Vector containing concentrated masses design variables
        self.add_param('m_desvar', val=np.zeros(len(m_desvar_list)))

        #Vector containing the concentrated masses' values
        self.add_output('m', val=np.zeros(self.mn))


    def solve_nonlinear(self, params, unknowns, resids):

        m_desvar_list = self.m_desvar_list

        m_indep = params['m_indep']
        m_desvar = params['m_desvar']

        m = m_indep

        #Substitute the design variables to create the thickness and mass vectors that are the inputs of Nastran components
        for i in range(len(m_desvar_list)):
            m[m_desvar_list[i]] = m_desvar[i]

        unknowns['m'] = m
