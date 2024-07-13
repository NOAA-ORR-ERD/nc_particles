"""
tests for particles
"""
from pathlib import Path
import numpy as np
import xarray as xr
import pytest


from nc_particles.particles import ParticleVariable, Particles


HERE = Path(__file__).parent
OUTPUT = HERE / 'temp_output'
sample_file = HERE / "sample_data" / "sample.nc"


def test_construction():
    """
    using internal representation, but what can you do?
    """
    # create an empty ragged array
    rows = [3, 5, 2, 7]
    ra = ParticleVariable.empty(rows)

    assert ra._data_array.shape == (sum(rows),)
    assert ra.dtype == np.dtype(np.float64)
    print(ra._data_array)

    ra = ParticleVariable.ones(rows, dtype=np.int32)
    print(ra._data_array)
    assert np.array_equal(ra._data_array, np.ones((sum(rows),), dtype=np.int32))
    assert ra.dtype == np.dtype(np.int32)

    ra = ParticleVariable.zeros(rows, dtype=np.float32)
    print(ra._data_array)
    assert np.array_equal(ra._data_array, np.zeros((sum(rows),), dtype=np.float32))
    assert ra.dtype == np.dtype(np.float32)


def test_indexing():
    """
    simple indexing -- should return a single row as a view
    """
    rows = [3, 5, 2, 7]

    ra = ParticleVariable.ones(rows, dtype=np.int32)

    for i, rl in enumerate(rows):
        row = ra[i]
        print(row)
        assert row.shape == (rl,)


def test_iteration():
    rows = [3, 5, 2, 7]

    ra = ParticleVariable.ones(rows, dtype=np.int32)

    for i, row in enumerate(ra):
        assert np.array_equal(row, np.ones((rows[i],), dtype=np.int32))


def test_init_from_data():
    rows = [3, 5, 2, 7]
    data = np.arange(sum(rows))
    ra = ParticleVariable(data, rows)

    assert np.array_equal(ra[2], [8, 9])


def test_init_from_bad_data():
    """
    init should raise if data wrong
    """
    rows = [3, 5, 2, 8]
    data = np.arange(sum(rows) - 1)
    with pytest.raises(ValueError):
        ra = ParticleVariable(data, rows)

    data = data = np.arange(sum(rows)).reshape((-1, 2))
    with pytest.raises(ValueError):
        ra = ParticleVariable(data, rows)


# tests of the Particles class
def test_init_particles_from_dataset():
    '''
    Tests that you can initialize from an xarray dataset
    '''
    ds = xr.open_dataset(sample_file)

    parts = Particles.from_dataset(ds)

    # print(parts.times)

    # print(f"{parts.times[0]=}")
    # print(f"{type(parts.times[0])}")

    assert parts.times.shape == (3,)
    # assert parts.times[0] == (3,)
    # assert parts.times[2] == (3,)

    assert parts.variables.keys() == {'latitude', 'depth', 'mass', 'longitude'}

    print(parts.variables['latitude'][1])

    # check variables

    # assert False

