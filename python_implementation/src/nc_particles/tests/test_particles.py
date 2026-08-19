"""
Tests for particles
"""
from datetime import UTC, datetime, timedelta
from math import nan
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from nc_particles.particles import Particles, ParticleVariable

pytestmark = pytest.mark.skip(reason="xarray integration not complete")

HERE = Path(__file__).parent
OUTPUT = HERE / 'temp_output'
sample_file = HERE / "sample_data" / "sample.nc"


def small_data_example():
    """
    example of ragged data.

    Discontinuous
    IDs are arbitrary: non-monotonically increasing

    """
    IDs = [17,  12,  3,  11,  13,  18,  5]

    full_form = [
        [   1,   2,    3,    4, nan, nan, nan ],
        [ nan,   5,  nan,    6, nan, nan, nan ],
        [ nan,   7,  nan,    8,   9,  10,  11 ],
        [ nan, nan,  nan,  nan,  12,  13,  14 ],
         ]

    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    pids = [[17, 12, 3, 11],
            [12, 11],
            [12, 17, 13, 18, 5],
            [13, 18, 5],
            ]
    return data, pids, IDs, full_form  # = small_data_example()

def small_data_example_full_variable():
    """
    Example of the same array, but in full xarray Variable form

    i.e with FillValue for the empty slots.

    Discontinuous
    IDs are arbitrary: non-monotonically increasing

    """
    data, pids, IDs, full_form = small_data_example() #noqa: RUF059
    full_var = xr.Variable(('time', 'pid'), full_form)

    return full_var


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

    ra = ParticleVariable.from_nested_data(data,
                                           particle_ids=pids,
                                           dtype=np.float32)

    # print(f"{ra._start_indexes=}")

    for row1, row2 in zip(data, ra):
        assert np.array_equal(row1, row2)
    # testing interenal structure -- but what can you do?
    for row1, row2 in zip(data, ra):
        assert np.array_equal(row1, row2)
    assert np.array_equal(ra._particle_ids,
                          [1, 2, 3, 4, 2, 4, 2, 4, 5, 6, 7, 5, 6, 7])


def test_from_nested_data_duplicate_id():
    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    pids = [[1, 2, 3, 4],
            [2, 4],
            [2, 4, 5, 6, 7],
            [5, 6, 6],
            ]
    with pytest.raises(ValueError):
        ra = ParticleVariable.from_nested_data(data,  # noqa:F841
                                               particle_ids=pids,
                                               dtype=np.float32)

def test_from_nested_data_no_ids():
    data = [[1, 2, 3, 4],
            [5, 6],
            [7, 8, 9, 10, 11],
            [12, 13, 14],
            ]
    # pids = [[1, 2, 3, 4],
    #         [2, 4],
    #         [2, 4, 5, 6, 7],
    #         [5, 6, 6],
    #         ]
    # with pytest.raises(ValueError):
    pv = ParticleVariable.from_nested_data(data)#,
                                           # particle_ids=pids,
                                           # dtype=np.float32)

    assert np.array_equal(pv._particle_ids,
                          [0, 1, 2, 3, 0, 1, 0, 1, 2, 3, 4, 0, 1, 2])



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

def test_append_row_no_ids():
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

    row = [15, 16, 17, 18, 19]

    ra.append_row(row)
    ids = [0, 1, 2, 3, 4]  # ids will fill in left aligned if not provided
    data.append(row)
    pids.append(ids)
    for row1, row2 in zip(data, ra):
        assert np.array_equal(row1, row2)

    assert np.array_equal(ra._particle_ids, [1, 2, 3, 4, 2, 4, 2, 4, 5, 6, 7, 5, 6, 7, 0, 1, 2, 3, 4])

    # non-unique
    ids = [0, 1, 2, 3, 3] 
    with pytest.raises(ValueError, match="particle_ids must be unique"):
        ra.append_row(row, ids)    

def test_shape():
    # make sure shape works for "wonky" IDs
    data, pids, IDs, full_form = small_data_example() #noqa: RUF059

    pv = ParticleVariable.from_nested_data(data, pids)

    print(pv)

    assert pv.shape == (4, 7)



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


def test_indexing_simple():
    """
    Simple indexing -- should return a single row
      of the right size.

    Default IDs, so all in sync -- and left aligned.
    """
    rows = [3, 5, 2, 7]

    ra = ParticleVariable.ones(rows, dtype=np.int32)

    for i, rl in enumerate(rows):
        row = ra[i]
        print(row)
        assert row.shape == (rl,)


def test_indexing_rows():
    """
    Single index -- should return a single row

    That row should have Fill Values where missing data is.
    """
    data, pids, IDs, full_form = small_data_example() #noqa: RUF059


    full_var = small_data_example_full_variable()

    pv = ParticleVariable.from_nested_data(data,
                                           particle_ids=pids,
                                           dtype=np.float64,
                                           FillValue=nan,
                                           dims=('time', 'pids')
                                           )

    for i, rl in enumerate(full_var):
        row = pv[i]
        print(f"{i=}")
        print(f"{rl=}")
        print(f"{row=}")
        assert np.array_equal(row, rl, equal_nan=True)

    assert False



def test_str():
    rows = [3, 5, 2, 7]
    ra = ParticleVariable.ones(rows, dtype=np.int32)

    string = str(ra)

    print("string:")
    print(string)

    assert string == """ParticleVariable:
1 1 1
1 1 1 1 1
1 1
1 1 1 1 1 1 1"""

def test__repr__():
    rows = [3, 5, 2, 7]
    ra = ParticleVariable.ones(rows, dtype=np.int32)

    string = repr(ra)

    print("string:")
    print(string)

    assert string == """ParticleVariable:
[1 1 1]
[1 1 1 1 1]
[1 1]
[1 1 1 1 1 1 1]"""

def test_iteration():
    rows = [3, 5, 2, 7]

    ra = ParticleVariable.ones(rows, dtype=np.int32)

    for i, row in enumerate(ra):
        assert np.array_equal(row, np.ones((rows[i],), dtype=np.int32))


def test_init_from_data():
    rows = [3, 5, 2, 7]
    data = np.arange(sum(rows))
    pv = ParticleVariable(data, rows)

    assert np.array_equal(pv[2], [8, 9])


def test_init_from_bad_data():
    """
    init should raise if data wrong
    """
    rows = [3, 5, 2, 8]
    # data array too small (substracted one)
    data = np.arange(sum(rows) - 1)
    with pytest.raises(ValueError):
        ra = ParticleVariable(data, rows)

    # data array wrong shape
    data = np.arange(sum(rows)).reshape((-1, 2))
    with pytest.raises(ValueError):
        ra = ParticleVariable(data, rows)
    # time var doesn't match
    data = np.arange(sum(rows))
    time = [datetime.now(tz=UTC) + timedelta(hours=i) for i in range(len(rows) + 1)]
    with pytest.raises(ValueError):
        ra = ParticleVariable(data, rows, time=time)  # noqa:F841


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

def test_as_full_array():
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

def test__build_index():
    """
    Testing the index of IDs to column number
    note: this is an implementation detail, so may need to be fixed
          if the implementaton
    """
#    data, pids = small_data_example()

    pids = [5, 2, 5, 6, 7, 23, 12, 5, 1, 2, 13, 8, 1, 14, 45, 23]

    result = [5, 2, 6, 7, 23, 12, 1, 13, 8, 14, 45]

    id_index = ParticleVariable._build_id_index(pids)
    # pv = ParticleVariable.from_nested_data(data,
    #                                        particle_ids=pids, dtype=np.float32)

    print(id_index)
    print([int(i) for i in id_index])
    print([int(i) for i in result])
    assert np.array_equal(list(id_index.keys()), result)

@pytest.mark.xfail(reason="not working yet")
def test_ParticleVariable_get_item():
    data, pids = small_data_example()

    pv = ParticleVariable.from_nested_data(data,
                                           particle_ids=pids, dtype=np.float32)

    # 1D indexing (getting a row)
    FV = pv._FillValue
    assert np.array_equal(pv[0], [1, 2, 3, 4, FV, FV, FV])
    assert np.array_equal(pv[1], [FV, 5, FV, 6, FV, FV, FV])

    # 2D indexing
    assert pv[1, 1] == 5


# tests of the Particles class
def test_init_particles_from_dataset():
    '''
    Tests that you can initialize from an xarray dataset
    '''
    ds = xr.open_dataset(sample_file)

    parts = Particles.from_dataset(ds)

    assert parts.time.shape == (3,)

    assert parts.variables.keys() == {'latitude', 'depth', 'mass', 'longitude'}

    # check variables
    lat = parts.variables['latitude']
    print(f"{type(lat)}")
    assert len(lat) == 3
    assert lat.shape == (3, 4)
    assert lat.dtype == np.float64


def test_init_particles_from_dataset_set_pc_var():
    '''
    Tests that you can initialize from an xarray dataset
    '''
    ds = xr.open_dataset(sample_file)
    parts = Particles.from_dataset(ds, particle_count_var='particle_count')

    assert parts.time.shape == (3,)

    assert parts.variables.keys() == {'latitude', 'depth', 'mass', 'longitude'}

    # check variables
    lat = parts.variables['latitude']
    print(f"{type(lat)}")
    assert len(lat) == 3
    assert lat.shape == (3, 4)
    assert lat.dtype == np.float64


def test_init_particles_from_dataset_missing_pc():
    '''
    Tests that you can initialize from an xarray dataset
    '''
    ds = xr.open_dataset(sample_file)
#    del ds['particle_count'].attrs['ragged_row_count']
    del ds['particle_count']
    with pytest.raises(ValueError):
        parts = Particles.from_dataset(ds)  # noqa:F841


def test_init_particles_from_dataset_specify_id():
    '''
    Tests that you can initialize from an xarray dataset
    '''
    ds = xr.open_dataset(sample_file)
    parts = Particles.from_dataset(ds, id_var='id')

    lat = parts.variables['latitude']
    assert len(lat) == 3
    assert lat.shape == (3, 4)
    assert lat.dtype == np.float64


def test_init_particles_from_dataset_missing_id():
    '''
    Tests that you can initialize from an xarray dataset
    '''
    ds = xr.open_dataset(sample_file)
    del ds['id']
    print(ds)
    with pytest.raises(ValueError):
        parts = Particles.from_dataset(ds)  # noqa:F841



def test_getitem():
    """
    should be able to index by variable name
    """
    parts = Particles.from_file(sample_file)

    print(parts.variables.keys())
    with pytest.raises(KeyError):
        assert parts['fred'] == 4

    mass = parts['mass']
    # not sure what else to test ...
    assert mass.shape == (3, 4)


def test_iter():
    """
    Iterating over the Particles object should yield the variable names
    (like a dict)
    """
    parts = Particles.from_file(sample_file)

    assert sorted(parts) == sorted(['latitude', 'depth', 'mass', 'longitude'])


def test_keys():
    parts = Particles.from_file(sample_file)
    assert sorted(parts.keys()) == sorted(['latitude', 'depth', 'mass', 'longitude'])


def test_dict_interface():
    """
    seems kludgy, but this should test that it all works :-)
    """
    parts = Particles.from_file(sample_file)
    assert list(zip(parts.keys(), parts.values())) == list(parts.items())


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

    fv = ParticleVariable._get_fill_value(np.dtype('<m8[ns]'))
    print(fv)
    assert np.isnat(fv)



