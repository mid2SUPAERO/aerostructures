# -*- coding: utf-8 -*-
"""
"""

from openmdao.api import ExplicitComponent

import numpy as np

class CaeroPlanform(ExplicitComponent):
    
    def __init__(self, y):
        super(CaeroPlanform, self).__init__()
        
        #Array containing the y coordinate of each section
        self.y = y
        
        #Number of CAERO cards (sections)
        self.n_sec = len(y)

    def setup(self):
        
        #root chord
        self.add_input('cr', val=1.)
        
        #break section chord
        self.add_input('cb', val=1.)
        
        #tip section
        self.add_input('ct', val=1.)
        
        #sweep angle
        self.add_input('sweep', val=1.)
        
        #root leading edge position
        self.add_input('xr', val=1.)
        
        #Vector of section chords
        self.add_output('c', val=np.zeros(self.n_sec))
        
        #Vector of section leading edge positions
        self.add_output('x_le', val=np.zeros(self.n_sec))
        
    def compute(self, inputs, outputs):
        
        n_sec = self.n_sec
        y = self.y
        cr = inputs['cr']
        cb = inputs['cb']
        ct = inputs['ct']
        sweep = inputs['sweep']
        xr = inputs['xr']
        
        c = np.zeros(self.n_sec)
        c[0] = cr
        c[1] = cb
        c[2] = cb - (cb-ct)/(y[3]-y[1])*(y[2]-y[1])
        c[3] = ct
        
        outputs['c'] = c
        
        outputs['x_le'] = xr*np.ones(n_sec) + np.tan(np.radians(sweep))*(y-y[0]*np.ones(n_sec))
