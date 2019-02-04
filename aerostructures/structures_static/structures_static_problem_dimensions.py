# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

class StaticStructureProblemDimensions:
    #Nastran template file
    template_file = 'nastran_static_template.inp'


    def __init__(self):
        #Dictionary containing the structural problem dimensions
        self.structure_dimensions = self.get_structure_dimensions()

        #List of structural nodes identification numbers (on the outer surface)
        self.node_id = self.structure_dimensions['node_id']

        #List of total structural nodes identification numbers (on the outer surface)
        self.node_id_all = self.structure_dimensions['node_id_all']

        #Number of different thickness regions
        self.tn = self.structure_dimensions['tn']

        #Number of concentrated masses
        self.mn = self.structure_dimensions['mn']

        #Number of stringer properties
        self.sn = self.structure_dimensions['sn']

        #Number of rod properties
        self.an = self.structure_dimensions['an']

        #Number of structural nodes on the outer surface
        self.ns = len(self.node_id)

        #Total number of structural nodes
        self.ns_all = len(self.node_id_all)

        #Number of Von Mises stress outputs
        self.n_stress = self.structure_dimensions['n_stress']


    #Function that returns the list of node IDs belonging to the outer surface
    def get_structure_dimensions(self):

        node_id = []
        node_id_all = []
        tn = 0
        mn = 0
        sn = 0
        an = 0
        n_stress = 0

        #Read the list of nodes belonging to the outer surface from the template file
        with open(self.template_file) as f:
            lines = f.readlines()

            outer_node_begin = lines.index('$List of nodes belonging to the outer skin\n')

            for i in range(len(lines)):
                #Store nodes belonging to the outer skin
                if i > outer_node_begin and lines[i][0] == '$':
                    node_id.append(lines[i].strip().lstrip('$'))

                else:
                    #Detect Nastran free field (comma separated) or small field (8 character)
                    if ',' in lines[i]:
                        line = lines[i].split(',')
                    else:
                        line = [lines[i][j:j+8] for j in range(0, len(lines[i]), 8)]

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
                    #Store number of different rod properties
                    elif line[0] == 'PROD':
                        an += 1
                    #Store number of stress outputs (2 stress values per surface, 1 stress value per rod)
                    elif line[0] == 'CTRIA3' or line[0] == 'CQUAD4':
                        n_stress += 2
                    elif line[0] == 'CROD':
                        n_stress += 1

        #Order nodes according to their ID and remove duplicates
        node_id_all = map(int, node_id_all)
        node_id_all = sorted(set(node_id_all))

        node_id = map(int, node_id)
        node_id = sorted(set(node_id))

        #Convert to string
        node_id_all = [str(node) for node in node_id_all]
        node_id = [str(node) for node in node_id]

        #Dictionary containing structure problem data
        structure_dimensions = {}
        structure_dimensions['node_id'] = node_id
        structure_dimensions['node_id_all'] = node_id_all
        structure_dimensions['tn'] = tn
        structure_dimensions['mn'] = mn
        structure_dimensions['sn'] = sn
        structure_dimensions['an'] = an
        structure_dimensions['n_stress'] = n_stress

        return structure_dimensions
