from setuptools import setup

setup(name='aerostructures',
      version='0.1',
      description='Aerostructural analysis using OpenMDAO',
      author='Joan Mas Colomer',
      author_email='joan.mas_colomer@onera.fr',
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
      install_requires=['openmdao==1.7.3'])
