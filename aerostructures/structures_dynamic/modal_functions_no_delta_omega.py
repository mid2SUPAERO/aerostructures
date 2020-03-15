# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import Component

#Component which computes scalar functions related to the difference between the reference and actual eigenvectors and eigenvalues
class ModalFunctions(Component):


    def __init__(self, node_id_all, N, M, mode_tracking=True):
        super(ModalFunctions, self).__init__()

        #Identification number of all the structural nodes
        self.node_id_all = node_id_all

        #Total number of structural nodes
        self.ns_all = len(node_id_all)

        #Number of normal modes to consider for the comparison
        self.N = N

        #Number of extracted normal modes
        self.M = M

        #Mode-tracking option
        self.mode_tracking = mode_tracking

        #Numpy array containing the M extracted normal modes
        self.add_param('phi', val=np.zeros((3*self.ns_all, self.M)))

        #Numpy array containing the N refernece normal modes
        self.add_param('phi_ref', val=np.zeros((3*self.ns_all, self.N)))

        #Vector containing the extracted eigenvalues
        self.add_param('eigval', val=np.zeros(M))

        #Vector containing the reference eigenvalues
        self.add_param('eigval_ref', val=np.zeros(N))

        #Total mass of the scaled model
        self.add_param('mass', val=0.)

        #Total mass of the reference model
        self.add_param('mass_ref', val=0.)

        #Frequency ratio between Full-Scale and scaled models
        self.add_param('omega_ratio', val=1.)

        #Mass ratio between Full-Scale and scaled models
        self.add_param('mass_ratio', val=1.)

        #Norm of the difference between the vectors containing reference and actual eigenvalues
        self.add_output('delta_omega', val=0.)

        #Absolute value of the difference between the scaled masses
        self.add_output('delta_mass', val=0.)

        #Reordered eigenvectors according to MAC values
        self.add_output('ord_phi', val=np.zeros((3*self.ns_all, self.N)))

        #Reordered eigenvalues according to MAC values
        self.add_output('ord_eigval', val=np.zeros(N))

        #MAC matrix trace
        self.add_output('MAC_trace', val=0.)


    def solve_nonlinear(self, params, unknowns, resids):

        phi = self.params['phi']

        phi_ref = self.params['phi_ref']

        eigval = self.params['eigval']

        eigval_ref = self.params['eigval_ref']

        mass = self.params['mass']

        mass_ref = self.params['mass_ref']

        omega_ratio = self.params['omega_ratio']

        mass_ratio = self.params['mass_ratio']

        N = self.N

        M = self.M

        mode_tracking = self.mode_tracking

        #Not use mode tracking iff mode_tracking is False
        if mode_tracking is not None and not mode_tracking:
            #Compute the Modal Assurance Criterion (MAC) matrix (square NxN)
            MAC = np.zeros((N,N))
            for i in range(N):
                for j in range(N):
                    MAC[i,j] = np.inner(phi_ref[:,i], phi[:,j])**2/(np.inner(phi_ref[:,i], phi_ref[:,i])*np.inner(phi[:,j], phi[:,j]))

            #Get the N first values
            ord_phi = phi[:,:N]
            ord_eigval = eigval[:N]
            ord_MAC = MAC

        else:
            #Compute the Modal Assurance Criterion (MAC) matrix (rectangular NxM)
            MAC = np.zeros((N,M))
            for i in range(N):
                for j in range(M):
                    MAC[i,j] = np.inner(phi_ref[:,i], phi[:,j])**2/(np.inner(phi_ref[:,i], phi_ref[:,i])*np.inner(phi[:,j], phi[:,j]))

            #List that defines the order of the eigenvectors in phi according to the eigenvectors in phi_ref based on the MAC value
            eig_order = []
            for i in range(N):
                eig_order.append(np.argmax(MAC[i,:]))

            #Reorder eigenvectors, eigenvalues, MAC and generalized masses according to the reference values
            ord_phi = np.zeros(phi_ref.shape)
            ord_eigval = np.zeros(eigval_ref.shape)
            ord_MAC = np.zeros((N,N))

            for i in range(N):
                ord_phi[:,i] = phi[:,eig_order[i]]
                ord_eigval[i] = eigval[eig_order[i]]
                ord_MAC[:,i] = MAC[:,eig_order[i]]

        #Compute the square of the L2 norm of the difference vector between the reference and actual radian frequencies
        omega_diff = np.sqrt(ord_eigval) - omega_ratio*np.sqrt(eigval_ref)
        delta_omega = np.linalg.norm(omega_diff)**2

        #Compute mass error
        delta_mass = mass - mass_ratio*mass_ref

        #Set the computed values as outputs
        unknowns['delta_omega'] = delta_omega

        unknowns['delta_mass'] = delta_mass

        unknowns['ord_phi'] = ord_phi

        unknowns['ord_eigval'] = ord_eigval

        unknowns['MAC_trace'] = ord_MAC.trace()
