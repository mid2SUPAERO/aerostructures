# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component


class XLeadingEdge(Component):

    def __init__(self, n_sec):
        super(XLeadingEdge, self).__init__()

        #Total number of sections defining the wing
        self.n_sec = n_sec

        #Coordinates y of all sections
        self.add_param('y_le', val=np.zeros(n_sec))

        #Chord length for all sections
        self.add_param('chords', val=np.zeros(n_sec))

        #Quarter-chord sweep angle for each segment
        self.add_param('sweep', val=np.zeros(self.n_sec - 1))

        #Wing offset in x direction
        self.add_param('xr', val=0.)

        #x Leadind edge coordinates of all sections
        self.add_output('x_le', val=np.zeros(n_sec))

    def solve_nonlinear(self, params, unknowns, resids):

        n_sec = self.n_sec

        y_le = params['y_le']
        chords = params['chords']
        sweep = params['sweep']
        xr = params['xr']

        x_le = np.zeros(n_sec)

        delta_y = np.zeros(n_sec - 1)
        delta_chords = np.zeros(n_sec - 1)

        for i in range(len(delta_y)):
            delta_y[i] = y_le[i+1] - y_le[i]

        for i in range(len(delta_chords)):
            delta_chords[i] = chords[i+1] - chords[i]

        delta_x_le = np.tan(np.radians(sweep))*delta_y - delta_chords/4.

        #Initialize x_le with the offset
        x_le[0] = xr
        for i in range(1, len(x_le)):
            x_le[i] = x_le[i-1] + delta_x_le[i-1]

        unknowns['x_le'] = x_le
