# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

class DynamicStructureProblemDimensions:
    #Nastran template file
    template_file = 'nastran_dynamic_template.inp'


    def __init__(self):
        #Dictionary containing the structural problem dimensions
        self.structure_dimensions = self.get_structure_dimensions()

        #List of total structural nodes identification numbers (on the outer surface)
        self.node_id_all = self.structure_dimensions['node_id_all']

        #Number of different thickness regions
        self.tn = self.structure_dimensions['tn']

        #Number of concentrated masses
        self.mn = self.structure_dimensions['mn']

        #Number of stringer properties
        self.sn = self.structure_dimensions['sn']

        #Total number of structural nodes
        self.ns_all = len(self.node_id_all)


    #Function that returns the list of node IDs belonging to the outer surface
    def get_structure_dimensions(self):

        node_id_all = []
        tn = 0
        mn = 0
        sn = 0

        #Read the list of nodes belonging to the outer surface from the template file
        with open(self.template_file) as f:
            lines = f.readlines()

            for line in lines:
                #Detect Nastran free field (comma separated) or small field (8 character)
                if ',' in line:
                    line = line.split(',')
                else:
                    line = [line[j:j+8] for j in range(0, len(line), 8)]

                #Remove blank spaces
                line = [word.strip() for word in line]

                #Store all structure nodes
                if line[0] == 'GRID':
                    node_id_all.append(line[1])

                #Store number of different thickness regions
                elif line[0] == 'PSHELL':
                    tn += 1
                #Store number of different concentrated masses
                elif line[0] == 'CONM2':
                    mn += 1
                #Store number of different stringer properties
                elif line[0] == 'PBAR':
                    sn += 1

        #Order total nodes according to their ID and remove duplicates
        node_id_all = map(int, node_id_all)
        node_id_all = sorted(set(node_id_all))

        #Convert to string
        node_id_all = [str(node) for node in node_id_all]

        #Dictionary containing structure problem data
        structure_dimensions = {}
        structure_dimensions['node_id_all'] = node_id_all
        structure_dimensions['tn'] = tn
        structure_dimensions['mn'] = mn
        structure_dimensions['sn'] = sn

        return structure_dimensions
