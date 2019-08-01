# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component


class WaveDrag(Component):

    def __init__(self):
        super(WaveDrag, self).__init__()

        #Flight Mach number
        self.add_param('Mach', val=0.)

        #Critical Mach number for wave drag
        self.add_param('Mcr', val=1.)

        #Wave drag coefficient
        self.add_output('CDw', val=0.)

    def solve_nonlinear(self, params, unknowns, resids):

        Mach = params['Mach']
        Mcr = params['Mcr']

        if Mach > Mcr:
            CDw = 20*(Mach - Mcr)**4
        else:
            CDw = 0.

        unknowns['CDw'] = CDw
