# -*- coding: utf-8 -*-
"""
"""

from openmdao.api import Component

import numpy as np

class CaeroPlanform(Component):
    
    def __init__(self, y):
        super(CaeroPlanform, self).__init__()
        
        #Array containing the y coordinate of each section
        self.y = y
        
        #Number of CAERO cards (sections)
        self.n_sec = len(y)
        
        #root chord
        self.add_param('cr', val=1.)
        
        #break section chord
        self.add_param('cb', val=1.)
        
        #tip section
        self.add_param('ct', val=1.)
        
        #sweep angle
        self.add_param('sweep', val=1.)
        
        #root leading edge position
        self.add_param('xr', val=1.)
        
        #Vector of section chords
        self.add_output('c', val=np.zeros(self.n_sec))
        
        #Vector of section leading edge positions
        self.add_output('x_le', val=np.zeros(self.n_sec))
        
    def solve_nonlinear(self, params, unknowns, resids):
        
        n_sec = self.n_sec
        y = self.y
        cr = params['cr']
        cb = params['cb']
        ct = params['ct']
        sweep = params['sweep']
        xr = params['xr']
        
        c = np.zeros(self.n_sec)
        c[0] = cr - (cr-cb)/y[1]*y[0]
        c[1] = cb
        c[2] = cb - (cb-ct)/(y[3]-y[1])*(y[2]-y[1])
        c[3] = ct
        
        unknowns['c'] = c
        
        unknowns['x_le'] = xr*np.ones(n_sec) + np.tan(np.radians(sweep))*y