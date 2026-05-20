#!/usr/bin/env python

"""
Test code for nc_particles

Not very complete

Designed to be run with pytest
"""

import os
from pathlib import Path

import pytest
import netCDF4
import nc_particles

HERE = Path(__file__).parent
OUTPUT = Path(__file__).parent / "output"

def test_init():
    """
    Can the classes be intitialized?
    """
    w = nc_particles.Writer(OUTPUT / 'junk_file.nc')
    del w
    print(os.getcwd())
    r = nc_particles.Reader(HERE / 'sample.nc')
    del r


def test_3_unlimited():
    with pytest.raises(ValueError):
        w = nc_particles.Writer(OUTPUT / 'junk_file.nc', nc_version=3)  # noqa:F841


def test_netcdf3():
    w = nc_particles.Writer(OUTPUT / 'junk_file.nc', num_timesteps=10, nc_version='3')
    w.close()
    nc = netCDF4.Dataset(OUTPUT / 'junk_file.nc')
    assert nc.file_format=='NETCDF3_CLASSIC'

def test_netcdf4():
    w = nc_particles.Writer(OUTPUT / 'junk_file.nc', num_timesteps=10, nc_version=4)
    w.close()
    nc = netCDF4.Dataset(OUTPUT / 'junk_file.nc')
    assert nc.file_format=='NETCDF4'

def test_netcdf_wrong():
    with pytest.raises(ValueError):
        w = nc_particles.Writer(OUTPUT / 'junk_file.nc', nc_version='nc4')  # noqa:F841

def test_netcdf_wrong_num():
    with pytest.raises(ValueError):
        w = nc_particles.Writer(OUTPUT / 'junk_file.nc', nc_version='5')  # noqa:F841


def test_multi_close():
    w = nc_particles.Writer(OUTPUT / 'junk_file.nc',
                            nc_version=4)
    w.close()
    w.close()
