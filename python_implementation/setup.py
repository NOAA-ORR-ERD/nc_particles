# setup.py for nc_particles

from setuptools import setup

setup(name='nc_particles',
      version='0.1.0',
      py_modules=['nc_particles'],
      requires=['numpy', 'netCDF4'],   # want other packages here?
      # metadata for upload to PyPI
      author="Christopher Barker",
      author_email="Chris.Barker@noaa.gov",
      description=("Code for reading and writing output from particle tracking models"),
      keywords="particle tracking",
      url="https://github.com/NOAA-ORR-ERD/nc_particles"
      )