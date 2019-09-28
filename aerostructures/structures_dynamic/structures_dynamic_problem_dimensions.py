# -*- coding: utf-8 -*-
"""
"""

from __future__ import print_function

class DynamicStructureProblemDimensions:


    def __init__(self, template_file):
        
        #Nastran template file
        self.template_file = template_file       
        
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
        
        #Number of rod properties
        self.an = self.structure_dimensions['an']

        #Total number of structural nodes
        self.ns_all = len(self.node_id_all)
        
        #Number of nodes in the horizontal direction of each section
        self.Ln = self.structure_dimensions['Ln']
        
        #Number of nodes in the vertical direction of each section
        self.Vn = self.structure_dimensions['Vn']


    #Function that returns the list of node IDs belonging to the outer surface
    def get_structure_dimensions(self):

        node_id_all = []
        tn = 0
        mn = 0
        sn = 0
        an = 0
        Ln = 0
        Vn = 0

        #Read the list of nodes belonging to the outer surface from the template file
        with open(self.template_file) as f:
            lines = f.readlines()
            
            try:
                mesh_para_line = lines.index('$Case parameters\n')
            except ValueError:
                mesh_para_line = -1
                Ln = 24
                Vn = 5

            for i in range(len(lines)):
                #Store nodes belonging to the outer skin
                
                if i == mesh_para_line:
                    line = lines[i+1].split(',')
                    Ln = float(line[2])
                    Vn = float(line[4])

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
        structure_dimensions['an'] = an
        structure_dimensions['Ln'] = Ln
        structure_dimensions['Vn'] = Vn

        return structure_dimensions
