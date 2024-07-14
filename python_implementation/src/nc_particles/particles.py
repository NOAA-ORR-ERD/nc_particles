"""
class to hold / work with output from particle tracking
models

The goal is that it can be read / written to various formats:

nc_particles, CF trajectory format, etc.
"""

import numpy as np
import xarray as xr

# name of the dimension for the ragged array data
# This should probably not be hard-coded
DATA_DIM_NAME = "data"


class Particles():
    """
    complete set of data with output from a particle tracking model
    """
    DATA_DIM_NAME = "data"
    @classmethod
    def from_file(cls, filename):
        """
        Create a Particles object from a file, in
        nc_particles format.

        Should support anything xarray does.
        """
        ds = xarray.open_dataset(filename)
        return cls.from_dataset(ds)

    @classmethod
    def from_dataset(cls,
                     dataset,
                     particle_count_var=None,
                     id_var=None,
                     ):
        """
        Create a Particles object from an xarray Dataset
        in nc_particles format
        """
        data_dim = DATA_DIM_NAME

        self = cls.__new__(cls)
        self.dataset = dataset  # keep a reference to the dataset

        self.times = dataset['time']
        time_dim = dataset.time.dims[0]
        if particle_count_var is not None:
            self._particle_count = dataset.variables[particle_count_var]
        else:
            # find particle_count variable
            for var in dataset.data_vars.values():
                if 'ragged_row_count' in var.attrs.keys():
                    self._particle_count = var
                    break
            else:
                # if not compliant, look for name
                try:
                    self._particle_count = dataset['particle_count']
                except KeyError:
                    raise ValueError("This is not a valid nc_particles file.\n"
                                     "input file does not have a particle_count variable."
                                     )
        # find the id variable
        if id_var is not None:
            self._particle_id = dataset.variables[id_var]
        else:
            for var in dataset.data_vars.values():
                if var.attrs['long_name'] == "particle ID":
                    self._particle_id = var
                    break
        if self._particle_id is None:  # still haven't found it
            try:
                self._particle_id = dataset.data_vars['id']
            except KeyError:
                raise ValueError("Couldn't find the particle ID variable."
                                 "It can be spedified with the keyword: `id_var`")


        # A few global parameters
        self.global_atttributes = dataset.attrs
        # build the variables
        self.variables = {}
        for var in dataset.data_vars.values():
            if var.name in {self._particle_id.name, self._particle_count.name}:
                continue
            if var.dims == (data_dim,):
                self.variables[var.name] = ParticleVariable(var,
                                                            self._particle_count,
                                                            self._particle_id,)

        # self.data_index = np.zeros((len(self.times) + 1,), dtype=np.int32)
        # self.data_index[1:] = np.cumsum(self.particle_count)
        # self.global_atttributes = {name: self.nc.getncattr(name) for name in self.nc.ncattrs()}

        return self




class ParticleVariable():
    """
    Ragged array class -- numpy-array-like to hold ragged array data.

    A ragged array is one in which the last dimension can have varying length "rows".

    e.g. NxX where X can vary.

    Currently only 2D, but should be extendable

    """
    # def __init__(self, var, particle_id, particle_counts):
    #     self._particle_id = particle_id
    #     super().__init__(var, particle_counts)

    def __init__(self, data, row_lengths, particle_ids=None, FillValue=None):
        """
        Initialize a RaggedArray from existing data.

        :param data: 1D array of data to be stored
        :param row_lengths: length of each individual row
               ``sum(row_lengths)`` should equal the length
               of the data array.
        :param particle_ids=None: IDs of the particles, so that you can track
                                  a particular particle. should be the same size and data.

        :param FillValue=None: value to use to fill the empty parts of the array
                                when returning a rectangular version. Defalts to
                                NaN for floats, and maxint for integer types.

        """
        data = xr.DataArray(data, dims=('data',))
        if data.ndim != 1:
            raise ValueError("input data array should be one dimensional.")
        if sum(row_lengths) != len(data):
            raise ValueError("``sum(row_lengths)`` must equal len(data).")
        self._data_array = data
        self._start_indexes = np.zeros((len(row_lengths) + 1,), dtype=np.int32)
        self._start_indexes[1:] = np.cumsum(row_lengths)
        if particle_ids is None:
            _particle_ids = np.zeros((len(data)), dtype=np.int32)
            for idx, rl in zip(self._start_indexes, row_lengths):
                _particle_ids[idx:idx+rl] = range(rl)
        else:
            _particle_ids = np.array(particle_ids, dtype=np.int32)

        self._particle_ids = xr.DataArray(_particle_ids, dims=('data',))

        self._FillValue = self._get_fill_value(data.dtype) if FillValue is None else FillValue

    @classmethod
    def from_nested_data(cls, data, *, dtype=np.float64, particle_ids=None, FillValue=None):
        """
        create a ParticleVariable for already nested data:

        data = [[1, 2, 3, 4],
                [5, 6],
                [7, 8, 9, 10, 11],
                [12, 13, 14],
                ]

        :param data: data as nested sequences

        :param dtype=None: data type of data

        :param particle_ids=None: IDs of particles -- should be same shape as the data.

        :param FillValue=None: Fill Value to use when making full arrays from data.
        """

        # unpack the data:
        row_lengths = []
        data_arr = []
        for row in data:
            data_arr.extend(row)
            row_lengths.append(len(row))
        if particle_ids is None:
            particle_ids_arr = None
        else:
            particle_ids_arr = []
            for pid in particle_ids:
                particle_ids_arr.extend(pid)
        data_arr = np.array(data_arr, dtype=dtype)
        return cls(data_arr, row_lengths, particle_ids_arr, FillValue)

    def append_row(self, row, particle_ids=None):
        """
        Add a new row to the data.
        :param row: the data for that timestep

        :param particle_ids: ids of the particle in that row
        """
        row = xr.DataArray(row, dims=('data',))
        if particle_ids is None:
            particle_ids = np.range(len(row), dtype=np.int32)
        else:
            particle_ids = np.array(particle_ids, dtype=np.int32)
        particle_ids = xr.DataArray(particle_ids, dims=('data',))
        self._particle_ids = xr.concat((self._particle_ids, particle_ids), 'data')
        self._data_array = xr.concat((self._data_array, row), 'data')
        end = self._start_indexes[-1] + len(row)
        self._start_indexes = np.append(self._start_indexes, end)

    @staticmethod
    def _get_fill_value(dtype):
        try:
             fv = np.iinfo(dtype).max
        except ValueError:
            try:
                np.finfo(dtype)
                fv = np.nan
            except ValueError as err:
                raise TypeError("dtype must be a numpy numerical data type") from err
        return fv

    @classmethod
    def empty(cls, row_lengths, dtype=np.float64, FillValue=None):
        """
        create an empty ragged array

        :param row_lengths: Sequence of row lengths. This is a full
                            specification of the shape and size.

        """
        self = cls.__new__(cls)
        self._data_array = xr.DataArray(np.empty((sum(row_lengths),), dtype=dtype),
                                        dims=('data',))
        # self._row_lengths = row_lengths
        self._start_indexes = np.zeros((len(row_lengths) + 1,), dtype=np.int32)
        self._start_indexes[1:] = np.cumsum(row_lengths)
        self._FillValue = self._get_fill_value(self._data_array.dtype) if FillValue is None else FillValue

        return self

    @classmethod
    def ones(cls, row_lengths, dtype=np.float64, FillValue=None):
        self = cls.empty(row_lengths, dtype)
        self._data_array[:] = 1
        return self

    @classmethod
    def zeros(cls, row_lengths, dtype=np.float64, FillValue=None):
        self = cls.empty(row_lengths, dtype)
        self._data_array[:] = 0
        return self

    @property
    def dtype(self):
        return self._data_array.dtype

    @property
    def __array__(self):
        arr = np.empty(self.shape, dtype=self.dtype)
        arr[:] = self._FillValue
        for i, row in enumerate(self):
            arr[i,:len(row)] = row
        return arr

    def __repr__(self):
        rep = ["Ragged Array:"]

        for row in self:
            rep.append(str(row))
        return "\n".join(rep)

    def __getitem__(self, indexes):
        # is it multiple indexes?
        if isinstance(indexes, tuple):
            time_ind = indexes[0]
            particle_index = indexes[1]
        else:
            try:
                ind = indexes.__index__()
            except AttributeError:
                # not a simple index
                raise NotImplementedError("multi-dim indexing not implimented yet")
            result = self._data_array[self._start_indexes[ind] : self._start_indexes[ind+1]]

        return result

    @property
    def shape(self):
        return (len(self), np.diff(self._start_indexes).max())

    def __len__(self):
        return len(self._start_indexes) - 1



# class ParticleVariable(RaggedArray):
#     """
#     Class to hold the data associated with a set of particles
#     """
#     def __init__(self, var, particle_id, particle_counts):
#         self._particle_id = particle_id
#         super().__init__(var, particle_counts)    

#     def __getitem__(self, indexes):
#         # is it multiple indexes?
#         if isinstance(indexes, tuple):
#             time_ind = indexes[0]
#             particle_index = indexes[1]
#         else:
#             return super().__getitem__(indexes)

#     def get_individual_particle(self, particle_id):
#         """
#         returns the data of an individual particle

#         :param particle_id: the id of the particle you want to track
#         """
#         # fixme: cache this somehow?
#         #        keep track of time?
#         indexes = np.where(self._particle_id[:] == particle_id)

#         return self._data_array[indexes]



