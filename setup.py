try:
    import setuptools
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name="cablab-core",
    version="0.1.0",
    description='CAB-LAB Data Cube Software',
    license='GPL 3',
    author='CAB-LAB Development Team',
    author_email='cablab@earthsystemdatacube.net',
    maintainer='Brockmann Consult GmbH',
    maintainer_email='cablab@earthsystemdatacube.net',
    url='http://earthsystemdatacube.net/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'cablab_cli = cablab.__main__:main',
        ],
        'cablab.converter.classes': [
            'lai = cablab.extensions:LaiConverter',
            'fapar = cablab.extensions:FaparConverter',
        ],
        'cablab.transformer.methods': [
            'lai = cablab.extensions:transform_lai',
            'fapar = cablab.extensions:transform_fapar',
        ],
    }
)
