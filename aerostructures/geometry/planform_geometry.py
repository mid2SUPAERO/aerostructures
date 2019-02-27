# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

class PlanformGeometry(ExplicitComponent):

    def setup(self, n_sec, b_sec):
        #Total number of sections defining the wing
        self.n_sec = n_sec

        #Number of the section of the wing break (1 is the root section)
        self.b_sec = b_sec

        #root chord
        self.add_input('cr', val=0.)

        #break section chord
        self.add_input('cb', val=0.)

        #tip section chord
        self.add_input('ct', val=0.)

        #sweep angle
        self.add_input('sweep', val=0.)

        #root leading edge position
        self.add_input('xr', val=0.)

        #Vector of section leading edge positions (spanwise)
        self.add_input('y_le', val=np.zeros(self.n_sec))

        #Vector of section chords
        self.add_output('chords', val=np.zeros(self.n_sec))

        #Vector of section leading edge positions
        self.add_output('x_le', val=np.zeros(self.n_sec))

    def compute(self, inputs, outputs):

        n_sec = self.n_sec
        b_sec = self.b_sec

        cr = inputs['cr']
        cb = inputs['cb']
        ct = inputs['ct']
        sweep = inputs['sweep']
        xr = inputs['xr']
        y_le = inputs['y_le']

        #Compute the x position of the leading edge of each section
        outputs['x_le'] = xr*np.ones(n_sec) + np.tan(np.radians(sweep))*(y_le-y_le[0]*np.ones(n_sec))

        #Compute the chord of each section
        #First, for the sections comprised between the root and the wing break
        c1 = (cb - cr)/(y_le[b_sec-1] - y_le[0])*(y_le[:b_sec] - y_le[0]*np.ones(b_sec)) + cr*np.ones(b_sec)
        c2 = (ct - cb)/(y_le[-1] - y_le[b_sec-1])*(y_le[b_sec:] - y_le[b_sec-1]*np.ones(n_sec-b_sec)) + cb*np.ones(n_sec-b_sec)

        chords = np.concatenate((c1, c2))

        outputs['chords'] = chords
