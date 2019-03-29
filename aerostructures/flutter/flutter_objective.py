# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent


class FlutterObj(ExplicitComponent):

    def __init__(self, N, F):
        super(FlutterObj, self).__init__()

        # Number of normal modes
        self.N = N

        # Number of reduced frequencies to consider
        self.F = F

    def setup(self):

        N = self.N
        F = self.F

        # Numpy array containing the real part of the F N by N aerodynamic coefficient matrices
        self.add_input('Qr', val=np.zeros((N, F*N)))

        # Numpy array containing the imaginary part of the F N by N aerodynamic coefficient matrices
        self.add_input('Qi', val=np.zeros((N, F*N)))

        # Numpy array containing the real part of the F N by N reference aerodynamic coefficient matrices
        self.add_input('Qr_ref', val=np.zeros((N, F*N)))

        # Numpy array containing the imaginary part of the F N by N reference aerodynamic coefficient matrices
        self.add_input('Qi_ref', val=np.zeros((N, F*N)))

        # Outout objective function value
        self.add_output('f', val=0.0)

    def compute(self, inputs, outputs):

        N = self.N
        F = self.F

        Q = np.zeros((N, F*N), dtype=complex)
        Q_ref = np.zeros((N, F*N), dtype=complex)

        Qr = inputs['Qr']
        Qi = inputs['Qi']
        Qr_ref = inputs['Qr_ref']
        Qi_ref = inputs['Qi_ref']

        Q.real = Qr
        Q.imag = Qi
        Q_ref.real = Qr_ref
        Q_ref.imag = Qi_ref

        Q_list = []
        Q_ref_list = []

        # Store each aerodynamic matrix (for each reduced frequency) into a list
        for i in range(F):
            Q_list.append(Q[:, N*i:N*i+N])
            Q_ref_list.append(Q_ref[:, N*i:N*i+N])

        norm = []

        # List that contains, for each reduced frequency, the Frobenius norm squared between the reference and current aerodynamic matrices
        for i in range(F):
            norm.append(np.linalg.norm(Q_list[i] - Q_ref_list[i])**2)

        # Objective function: Sum of the norms for all reduced frequencies
        f = sum(norm)

        outputs['f'] = f
