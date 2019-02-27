# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

import numpy as np

from openmdao.api import ExplicitComponent

#ExplicitComponent which computes scalar functions related to the difference between the reference and actual eigenvectors and eigenvalues
class ModalFunctions(ExplicitComponent):


    def setup(self, node_id_all, N, M, mode_tracking=True):
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
        self.add_input('phi', val=np.zeros((3*self.ns_all, self.M)))

        #Numpy array containing the N refernece normal modes
        self.add_input('phi_ref', val=np.zeros((3*self.ns_all, self.N)))

        #Vector containing the extracted eigenvalues
        self.add_input('eigval', val=np.zeros(M))

        #Vector containing the reference eigenvalues
        self.add_input('eigval_ref', val=np.zeros(N))

        #Total mass of the scaled model
        self.add_input('mass', val=0.)

        #Total mass of the reference model
        self.add_input('mass_ref', val=0.)

        #Frequency ratio between Full-Scale and scaled models
        self.add_input('omega_ratio', val=1.)

        #Mass ratio between Full-Scale and scaled models
        self.add_input('mass_ratio', val=1.)

        #Difference between the vectors containing reference and actual frequencies
        self.add_output('delta_omega', val=np.zeros(N))

        #Absolute value of the difference between the scaled masses
        self.add_output('delta_mass', val=0.)

        #Reordered eigenvectors according to MAC values
        self.add_output('ord_phi', val=np.zeros((3*self.ns_all, self.N)))

        #Reordered eigenvalues according to MAC values
        self.add_output('ord_eigval', val=np.zeros(N))

        #MAC matrix trace
        self.add_output('MAC_trace', val=0.)


    def compute(self, inputs, outputs):

        phi = inputs['phi']

        phi_ref = inputs['phi_ref']

        eigval = inputs['eigval']

        eigval_ref = inputs['eigval_ref']

        mass = inputs['mass']

        mass_ref = inputs['mass_ref']

        omega_ratio = inputs['omega_ratio']

        mass_ratio = inputs['mass_ratio']

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
        delta_omega = np.sqrt(ord_eigval) - omega_ratio*np.sqrt(eigval_ref)

        #Compute mass error
        delta_mass = mass - mass_ratio*mass_ref

        #Set the computed values as outputs
        outputs['delta_omega'] = delta_omega

        outputs['delta_mass'] = delta_mass

        outputs['ord_phi'] = ord_phi

        outputs['ord_eigval'] = ord_eigval

        outputs['MAC_trace'] = ord_MAC.trace()
