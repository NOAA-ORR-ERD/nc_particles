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

def test_from_nested_data():
    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    pids = [[1, 2, 3, 4],
            [2, 4],
            [2, 4, 5, 6, 7],
            [5, 6, 7],
            ]

    ra = ParticleVariable.from_nested_data(data, particle_ids=pids, dtype=np.float32)

    # print(f"{ra._start_indexes=}")

    for row1, row2 in zip(data, ra):
        assert np.array_equal(row1, row2)
    # testing interenal structure -- but what can you do?
    for row1, row2 in zip(data, ra):
        assert np.array_equal(row1, row2)
    assert np.array_equal(ra._particle_ids, [1, 2, 3, 4, 2, 4, 2, 4, 5, 6, 7, 5, 6, 7])

def test_append_row():
    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    pids = [[1, 2, 3, 4],
            [2, 4],
            [2, 4, 5, 6, 7],
            [5, 6, 7],
            ]

    row = [15, 16, 17, 18, 19]
    row_pids = [5, 7, 8, 9, 10]
    ra = ParticleVariable.from_nested_data(data, particle_ids=pids, dtype=np.float32)

    ra.append_row(row, row_pids)

    data.append(row)
    pids.append(row_pids)
    for row1, row2 in zip(data, ra):
        assert np.array_equal(row1, row2)

    assert np.array_equal(ra._particle_ids, [1, 2, 3, 4, 2, 4, 2, 4, 5, 6, 7, 5, 6, 7, 5, 7, 8, 9, 10])

def test__array__():
    """
    The __array__ property should return a regular old numpy array

    In this case, it will be a left aligned rectangular array.

    ._FillValue is used to fill the empty space.
    """
    rows = [3, 5, 2, 7]

    fv = 2147483647
    filled = np.array([[1,  1,  1, fv, fv, fv, fv],
                       [1,  1,  1,  1,  1, fv, fv],
                       [1,  1, fv, fv, fv, fv, fv],
                       [1,  1,  1,  1,  1,  1,  1],
                       ], dtype=np.int32)

    ra = ParticleVariable.ones(rows, dtype=np.int32)

    arr = ra.__array__

    assert isinstance(arr, np.ndarray)

    print(filled)
    print(arr)
    assert np.array_equal(arr, filled)



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


def test_get_by_id():
    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    pids = [[1, 2, 3, 4],
            [2, 4],
            [2, 4, 5, 6, 7],
            [5, 6, 7],
            ]

    ra = ParticleVariable.from_nested_data(data, particle_ids=pids, dtype=np.float32)

    particle_data = ra.get_by_id(2)
    assert np.array_equal(particle_data, [2, 5, 7, np.nan], equal_nan=True)

    particle_data = ra.get_by_id(7)
    assert np.array_equal(particle_data, [np.nan, np.nan, 11, 14], equal_nan=True)

def test_get_full_array():
    """
    Returns a full array, matching the particle IDs, and
    filling the missing values with FillValue
    """
    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    pids = [[1, 2, 3, 4],
            [2, 4],
            [2, 4, 5, 6, 7],
            [5, 6, 7],
            ]

    full_pid  =  [     1,      2,      3,      4,      5,      6,      7]
    full_data = [[     1,      2,      3,      4, np.nan, np.nan, np.nan],
                 [np.nan,      5, np.nan,      6, np.nan, np.nan, np.nan],
                 [np.nan,      7, np.nan,      8,      9,     10,     11],
                 [np.nan, np.nan, np.nan, np.nan,   12,     13,     14],
                 ]

    ra = ParticleVariable.from_nested_data(data, particle_ids=pids, dtype=np.float32)

    f_pids, full = ra.as_full_array()

    assert full.shape == (4, 7)
    assert np.array_equal(f_pids, full_pid)
    assert np.array_equal(full, full_data, equal_nan=True)


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

    assert parts.variables.keys() == {'latitude', 'depth', 'mass', 'longitude'}

    # check variables
    lat = parts.variables['latitude']
    print(f"{type(lat)}")
    assert len(lat) == 3
    assert lat.shape == (3, 4)
    assert lat.dtype == np.float64


def test_get_fill_value():
    fv = ParticleVariable._get_fill_value(np.float64)
    print(fv)
    assert np.isnan(fv)

    fv = ParticleVariable._get_fill_value(np.float32)
    print(fv)
    assert np.isnan(fv)

    fv = ParticleVariable._get_fill_value(np.int32)
    print(fv)
    assert fv == 2147483647

    fv = ParticleVariable._get_fill_value(np.uint8)
    print(fv)
    assert fv == 255

