#!/usr/bin/env python

"""
Test code for nc_particles

Not very complete

Designed to be run with pytest

"""
from pathlib import Path

import os

import pytest
import netCDF4
from nc_particles import nc_particles

HERE = Path(__file__).parent
OUTPUT = HERE / 'temp_output'
sample_file = HERE / "sample_data" / "sample.nc"

def test_init():
    """
    Can the classes be intitialized?
    """
    w = nc_particles.Writer(OUTPUT / 'junk_file.nc')
    del w
    print(os.getcwd())
    nc_particles.Reader(sample_file)


def test_3_unlimited():
    with pytest.raises(ValueError):
        nc_particles.Writer(OUTPUT / 'junk_file2.nc', nc_version=3)


def test_netcdf3():
    w = nc_particles.Writer(OUTPUT / 'junk_file3.nc', num_timesteps=10, nc_version='3')
    w.close()
    nc = netCDF4.Dataset(OUTPUT / 'junk_file3.nc')
    assert nc.file_format == 'NETCDF3_CLASSIC'


def test_netcdf4():
    w = nc_particles.Writer(OUTPUT / 'junk_file4.nc', num_timesteps=10, nc_version=4)
    w.close()
    nc = netCDF4.Dataset(OUTPUT / 'junk_file4.nc')
    assert nc.file_format == 'NETCDF4'


def test_netcdf_wrong():
    with pytest.raises(ValueError):
        nc_particles.Writer(OUTPUT / 'junk_file.nc', nc_version='nc4')

@pytest.mark.skip("file is left open")
def test_netcdf_wrong_num():
    with pytest.raises(ValueError):
        nc_particles.Writer(OUTPUT / 'junk_file.nc', nc_version='5')


def test_multi_close():
    w = nc_particles.Writer(OUTPUT / 'junk_file5.nc',
                            nc_version=4)
    w.close()
    w.close()
