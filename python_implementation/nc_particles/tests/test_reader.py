import os
import datetime
from pathlib import Path
import gc


import pytest
import numpy as np
import netCDF4
import nc_particles

HERE = Path(__file__).parent


## test the Reader
def test_read_required():
    """
    Does it find the required variables and attributes
    Should be able to set up data_index
    """
    r = nc_particles.Reader(HERE / 'sample.nc')
    assert len(r.times) == 3
    assert np.array_equal(r.data_index, np.array([0, 3, 7, 9]))
    r.close()

def test_read_existing_dataset():
    nc = netCDF4.Dataset(HERE / 'sample.nc')
    r = nc_particles.Reader(nc)
    assert len(r.times) == 3
    r.close()

def test_str():
    r = nc_particles.Reader(HERE / 'sample.nc')
    s = str(r)
    r.close()
#     nc_particles Reader object:
#     variables: ['latitude', 'depth', 'mass', 'id', 'longitude']
#     number of timesteps: 3
    assert "timesteps: 3" in s
    assert s.startswith("nc_particles Reader object:")


## other tests fail (E   RuntimeError: NetCDF: Not a valid ID)
## if this test is here -- no idea why, but I think NetCDF4 isn't cleaning up after itself well
def test_read_variables():
    """
    does it find the data variables ?
    """
    r = nc_particles.Reader(HERE / 'sample.nc')
    # set(), because order doesn't matter
    varnames = set(r.variables)
    r.close()
    assert varnames == set(['latitude', 'depth', 'mass', 'id', 'longitude'])

def test_get_all_timesteps():
    gc.collect()  # very much should not be necceary, but netCDF4 does not clean up after itself well.
    r = nc_particles.Reader(HERE / 'sample.nc')
    data = r.get_all_timesteps(variables=['depth', 'mass', 'id'])
    r.close()
    print(len(data['depth']))
    assert 'depth' in data
    assert 'mass' in data
    assert 'id' in data
    for name, val in data.items():
        assert len(val) == 3
    ## better to check actual data, but what can you do?

def test_get_timestep():
    r = nc_particles.Reader(HERE / 'sample.nc')
    data = r.get_timestep(2, variables=['latitude', 'depth', 'mass', 'id', 'longitude'])
    r.close()
    # specific results from the sample file
    assert np.array_equal(data['longitude'], [-88.3, -88.1])
    assert np.array_equal(data['latitude'], [28.1, 28.0])
    assert np.array_equal(data['depth'], [0.0, 0.1])
    assert np.array_equal(data['mass'], [0.05, 0.06])
    assert np.array_equal(data['id'], [1, 3])

def test_get_individual_trajectory():
    r = nc_particles.Reader(HERE / 'sample.nc')
    
    path = r.get_individual_trajectory(1)
    r.close()
    assert np.array_equal(path['latitude'],  [28.0, 28.05, 28.1])
    assert np.array_equal(path['longitude'], [-88.1, -88.2, -88.3])


def test_get_units():
    r = nc_particles.Reader(HERE / 'sample.nc')
    assert r.get_units('depth') == 'meters'
    assert r.get_units('longitude') == 'degrees_east'
    r.close()


def test_get_attributes():
    r = nc_particles.Reader(HERE / 'sample.nc')

    assert  r.get_attributes('depth') == {'units' : "meters",
                                          'long_name' : "particle depth below sea surface",
                                          'standard_name' : "depth",
                                          'axis' : "z positive down",
                                          }
    r.close()
