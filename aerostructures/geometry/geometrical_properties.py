# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 14:44:46 2019

@author: @Giovanni Quaglia
"""

from __future__ import print_function

import numpy as np

class GeometricalProperties:
    
    def __init__(self,Ln,Vn,tn,an,sn,t_0,l_0,s_0_tot,Ix_0_tot,Iy_0_tot) :
        
        #Number of nodes in the horizontal direction of each section
        self.Ln = Ln
        
        #Number of nodes in the vertical direction of each section
        self.Vn = Vn
        
        #Number of regions where the thicknesses are defined
        self.tn = tn

        #Number of stringer sections
        self.sn = sn

        #Number of rod sections
        self.an = an
        
        #Original values of thickness for shell elements
        self.t_0 = t_0
        
        #Amplitude of longerons heads
        self.l_0 = l_0
        
        #Total section of stringers and stiffeners
        self.s_0_tot = s_0_tot
        
        #Total first moment of inertia of stringers and stiffeners
        self.Ix_0_tot = Ix_0_tot
        
        #Total second moment of inertia of stringers and stiffeners
        self.Iy_0_tot = Iy_0_tot
        
        #Dictionary containing the geometrical parameters
        self.geom_params = self.get_geometrical_params()
        
        #Values of thickness for shell elements
        self.t = self.geom_params['t']
        
        #Values of cross sectional area for rod elements
        self.a = self.geom_params['a']
        
        #Values of cross sectional area for bar elements
        self.s = self.geom_params['s']
        
        #Values of first moment of inertia for bar elements
        self.Ix = self.geom_params['Ix']
        
        #Values of second moment of inertia for bar elements
        self.Iy = self.geom_params['Iy']
        
        
    #Function that returns the structural parameters from a Nastran input file
    def get_geometrical_params(self):
        
        t = np.zeros(self.tn)
        a = np.zeros(self.an)
        s = np.zeros(self.sn)
        Ix = np.zeros(self.sn)
        Iy = np.zeros(self.sn)
        
        
        t = self.t_0
        
        for i in range(len(a)):
            a[i] = self.l_0[i]*t[i+6]
            
        for i in range(len(s)):
            if i == 2 or i == 3 or i == 5:
                s[i] = self.s_0_tot[i]
                Ix[i] = self.Ix_0_tot[i]
                Iy[i] = self.Iy_0_tot[i]
            elif i == 6 or i == 7:
                s[i] = self.s_0_tot[i]/(self.Ln)
                Ix[i] = self.Ix_0_tot[i]/(self.Ln)
                Iy[i] = self.Iy_0_tot[i]/(self.Ln)                
            else:
                s[i] = self.s_0_tot[i]/(self.Ln-2)
                Ix[i] = self.Ix_0_tot[i]/(self.Ln-2)
                Iy[i] = self.Iy_0_tot[i]/(self.Ln-2)
        
        geometrical_params = {}
        geometrical_params['t'] = t
        geometrical_params['a'] = a
        geometrical_params['s'] = s
        geometrical_params['Ix'] = Ix
        geometrical_params['Iy'] = Iy
        

        return geometrical_params
        
        





