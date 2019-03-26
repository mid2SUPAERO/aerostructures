from setuptools import setup

setup(name='aerostructures',
      version='1.0',
      description='Aerostructural analysis using OpenMDAO',
      author='Joan Mas Colomer',
      author_email='joan.mas-colomer2@isae-supaero.fr>',
      packages=['aerostructures',
				'aerostructures.aerodynamics',
                    'aerostructures.data_transfer',
				'aerostructures.flutter',
				'aerostructures.geometry',
				'aerostructures.number_formatting',
                'aerostructures.openmdao_tools',
                    'aerostructures.solvers',
				'aerostructures.structures_dynamic',
				'aerostructures.structures_static'],
      install_requires=['openmdao>=1.7.3', 'pyNastran'])
