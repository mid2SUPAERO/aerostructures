# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

class WingSegmentProps(Component):

    def __init__(self, n_sec):
        super(WingSegmentProps, self).__init__()

        #Total number of sections defining the wing
        self.n_sec = n_sec

        #Coordinates x and y of the leading edge for all sections
        self.add_param('x_le', val=np.zeros(n_sec))
        self.add_param('y_le', val=np.zeros(n_sec))

        #Thickness-to-chord ratio for all sections
        self.add_param('tc', val=np.zeros(n_sec))

        #Chord length for all sections
        self.add_param('chords', val=np.zeros(n_sec))

        #Average thickness-to-chord ratio for each wing segment (spanwise)
        self.add_output('tc_segment', val=np.zeros(self.n_sec - 1))

        #Quarter-chord sweep angle for each segment
        self.add_output('sweep_segment', val=np.zeros(self.n_sec - 1))

        #Projected area of each segment
        self.add_output('area_segment', val=np.zeros(self.n_sec - 1))

    def solve_nonlinear(self, params, unknowns, resids):

        n_sec = self.n_sec

        x_le = params['x_le']
        y_le = params['y_le']
        tc = params['tc']
        chords = params['chords']
        
        tc_segment = np.zeros(n_sec - 1)

        for i in range(len(tc_segment)):
            tc_segment[i] = (tc[i] + tc[i+1])/2

        delta_y = np.zeros(n_sec - 1)

        for i in range(len(delta_y)):
            delta_y[i] = y_le[i+1] - y_le[i]

        #Position of the quarter chord for each section
        x_c_4 = x_le + chords/4.

        delta_x_c_4 = np.zeros(n_sec - 1)

        for i in range(len(delta_x_c_4)):
            delta_x_c_4[i] = x_c_4[i+1] - x_c_4[i]

        sweep_segment = np.degrees(np.arctan(delta_x_c_4/delta_y))

        area_segment = np.zeros(n_sec - 1)

        for i in range(len(area_segment)):
            area_segment[i] = (chords[i] + chords[i+1])/2*delta_y[i]

        unknowns['tc_segment'] = tc_segment
        unknowns['sweep_segment'] = sweep_segment
        unknowns['area_segment'] = area_segment
