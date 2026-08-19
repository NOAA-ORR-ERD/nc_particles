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


class Particles:
    """
    complete set of data with output from a particle tracking model
    
    This is "ducked typed" to act like an xarrray dataset.
    """
    DATA_DIM_NAME = "data"
    @classmethod
    def from_file(cls, filename):
        """
        Create a Particles object from a file, in
        nc_particles format.

        Should support anything xarray does.
        """
        ds = xr.open_dataset(filename)
        return cls.from_dataset(ds)

    @classmethod
    def from_dataset(cls,
                     dataset,
                     particle_count_var=None,
                     id_var=None,
                     time_var=None
                     ):
        """
        Create a Particles object from an xarray Dataset
        in nc_particles format

        :param dataset: The xarray dataset to use

        :param particle_count_var: the name of the variable that
                                   provides the particle count
                                   (length of each row)

        :param id_var: name of variable that provides the particle IDs
        :param time_var: name of time variable
        """
        data_dim = DATA_DIM_NAME

        self = cls.__new__(cls)
        self.dataset = dataset  # keep a reference to the dataset

        time_var = 'time' if time_var is None else time_var
        self.time = dataset[time_var]
        # time_dim = dataset.time.dims[0]

        if particle_count_var is not None:
            self._particle_count = dataset[particle_count_var]
        else:
            # find particle_count variable
            for var in dataset.data_vars.values():
                if 'ragged_row_count' in var.attrs:
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
        self._particle_id = None
        if id_var is not None:
            self._particle_id = dataset[id_var]
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
                self.variables[var.name] = ParticleVariable(data=var,
                                                            row_lengths=self._particle_count,
                                                            particle_ids=self._particle_id,
                                                            time=self.time,
                                                            )

        # self.data_index = np.zeros((len(self.time) + 1,), dtype=np.int32)
        # self.data_index[1:] = np.cumsum(self.particle_count)
        # self.global_atttributes = {name: self.nc.getncattr(name) for name in self.nc.ncattrs()}

        return self

    def __getitem__(self, key):
        """
        Indexes by variable name, like a dict.
        """
        return self.variables[key]

    def __iter__(self):
        """
        Iteration is iterating teh dict of variables
        """
        return iter(self.variables)

    def keys(self):
        return self.variables.keys()

    def values(self):
        return self.variables.values()

    def items(self):
        return self.variables.items()

    def to_rectangular(self):
        """
        returns an xarray.Dataset that has all the particle data in a
        "rectangular" format:

        (time, particle)

        Missing data are filled in with _FillValue

        particle_id is a 1D array
        """
        # Start with a new dataset:
        # rect_ds = self.dataset.copy()

        # Then replace the arrays
        raise NotImplementedError


class ParticleVariable:
    """
    xarray-Variable-like that holds the data associated with the particles
    """

    def __init__(self,
                 data,
                 row_lengths,
                 time=None,
                 particle_ids=None,
                 FillValue=None,
                 attrs=None,
                 name='',
                 dims=('time', 'particle_ids')):
        """
        Initialize a ParticleVariable from existing data.

        :param data: 1D array of data to be stored
        :param row_lengths: length of each individual row
               ``sum(row_lengths)`` should equal the length
               of the data array.
        :param particle_ids=None: IDs of the particles, so that you can track
                                  a particular particle. should be the same size and data.
                                  If None, IDs will be assigned assuming data are left-aligned.

        :param FillValue=None: value to use to fill the empty parts of the array
                                when returning a rectangular version. Defalts to
                                NaN for floats, and maxint for integer types.

        :param attrs=None: attributes associated with the data, e.g. units, etc.
        :type attrs: Mapping

        :param dims=('time', 'particle_ids'): dimension names
        :type dims: tuple[str]
        """

        data = np.asarray(data)

        if len(data.shape) != 1:
            raise ValueError("input data array should be one dimensional.")
        if sum(row_lengths) != len(data):
            raise ValueError("``sum(row_lengths)`` must equal len(data).")
        if time is not None and len(row_lengths) != len(time):
            raise ValueError("number of rows must equal number of times")
        # FixMe -- should be specified?
        self.dims = dims
        self._time = time
        self._data_array = data
        self._start_indexes = np.zeros((len(row_lengths) + 1,), dtype=np.int32)
        self._start_indexes[1:] = np.cumsum(row_lengths)
        if particle_ids is None:
            _particle_ids = np.zeros((len(data)), dtype=np.int32)
            for idx, rl in zip(self._start_indexes, row_lengths):
                _particle_ids[idx:idx + rl] = range(rl)
        else:
            _particle_ids = np.array(particle_ids, dtype=np.int32)

        self._particle_ids = _particle_ids
        self._FillValue = (self._get_fill_value(data.dtype)
                           if FillValue is None else FillValue)
        self._id_row_index = self._build_id_index(self._particle_ids)
        self.attrs = attrs if attrs is not None else {}
        self.name = name


    @classmethod
    def from_nested_data(cls,
                         data,
                         *,
                         dtype=np.float64,
                         particle_ids=None,
                         FillValue=None,
                         attrs=None,
                         dims=None
                         ):
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

        :param attrs=None: attributes associated with the data, e.g. units, etc.
        :type attrs: Mapping

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
                if len(np.unique(pid)) != len(pid):
                    raise ValueError("particle_ids must be unique")
                particle_ids_arr.extend(pid)
        data_arr = np.array(data_arr, dtype=dtype)
        return cls(data=data_arr,
                   row_lengths=row_lengths,
                   particle_ids=particle_ids_arr,
                   FillValue=FillValue,
                   attrs=attrs,
                   dims=dims,
                   )

    @staticmethod
    def _build_id_index(ids):
        """
        builds the index of IDs to column numbers

        preserves the order of the IDs
            (necessary? maybe not, but seems like a good UI)
        """
        ids = np.asarray(ids)
        vals, idx = np.unique(ids, sorted=True, return_index=True)
        unique_ids = vals[np.argsort(idx)]

        id_index = {idx: j for j, idx in enumerate(unique_ids)}

        return id_index

    def append_row(self, row, particle_ids=None):
        """
        Add a new row to the data.
        :param row: the data for that timestep

        :param particle_ids: ids of the particle in that row
        """
        row = np.asarray(row)
        if particle_ids is None:
            particle_ids = np.arange(len(row), dtype=np.int32)
        else:
            particle_ids = np.array(particle_ids, dtype=np.int32)
        if len(np.unique(particle_ids)) != len(particle_ids):
            raise ValueError("particle_ids must be unique")
        self._particle_ids = np.concat((self._particle_ids, particle_ids), axis=0)
        self._data_array = np.concat((self._data_array, row), axis=0)
        end = self._start_indexes[-1] + len(row)
        self._start_indexes = np.append(self._start_indexes, end)

    def get_by_id(self, pid):
        """
        Return a full 1D array of the data corresponding to a particle id

        :param id: the id of the particle the data is for

        returns 1D array, with any missing data replaced by the FillValue
        """
        # NOTE: this is not very optimized, there may be a better way
        path = np.empty((len(self),), dtype=self.dtype)
        path[:] = self._FillValue
        for idx in range(len(self._start_indexes) - 1):
            start, end = self._start_indexes[idx], self._start_indexes[idx+1]
            row = self._data_array[start:end]
            ids = self._particle_ids[start:end]
            try:
                path[idx] = row[np.where(ids==pid)][0]
            except IndexError: # nothing there, move on.
                pass
        return path

    def as_full_array(self):
        """
        Return a full 2D array of the data, with the particle ids
        aligned.

        Returns: ids, full_array
            ids is 1-d array of the ids corresponding to the columns
            full_array is a 2D array, with any missing data replaced by the FillValue
        """
        # NOTE: this is not very optimized, there may be a better way
        #       and could certainly be optimized for the special case
        #       of a dense array
        all_ids = np.unique(self._particle_ids)
        full_arr = np.full((len(self), len(all_ids)), self._FillValue, dtype = self.dtype)
        for idx, id in enumerate(all_ids):
            full_arr[:, idx] = self.get_by_id(id)
        coords = {"time": self._time,
                  "particles": all_ids}
        # full_da = xr.Variable(["time", "particles"],
        #                       full_arr,
        #                       attrs=self.attrs
        #                       )
        full_da = xr.Variable(data=full_arr,
                              coords=coords,
                              dims=None, # should figure it out?
                              name=self.name,  # give it a name?
                              attrs=self.attrs,
                              indexes=None,  # not sure what these are
                              fastpath=False)
        return all_ids, full_da

    @staticmethod
    def _get_fill_value(dtype):
        try:
            if issubclass(dtype.type, (np.datetime64, np.timedelta64)):
                fv = np.array('NaT', dtype=dtype)
                return fv
        except AttributeError:
            # not a datetime dtype -- really not sure how that works!
            pass

        try:
             fv = np.iinfo(dtype).max
        except ValueError:
            try:
                np.finfo(dtype)
                fv = np.nan
            except ValueError as err:
                raise TypeError("dtype must be a numpy numerical or datetime64 data type") from err
        return fv

    @classmethod
    def empty(cls,
              row_lengths,
              dtype=np.float64,
              FillValue=None,
              time=None,
              dims=('time', 'particle_ids'),
              ):
        """
        create an empty ParticleVariable

        :param row_lengths: Sequence of row lengths. This is a full
                            specification of the shape and size.

        """
        data = np.empty((sum(row_lengths),), dtype=dtype)

        return cls(data,
                   row_lengths,
                   time=None,
                   particle_ids=None,
                   FillValue=FillValue,
                   attrs=None,
                   name='',
                   dims=dims)

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
        rep = ["ParticleVariable:"]
        for row in self:
            rep.append(str(row.data))
        return "\n".join(rep)

    def __str__(self):
        rep = ["ParticleVariable:"]
        for row in self:
            rep.append(str(row.data)[1:-1])
        return "\n".join(rep)

    def __getitem__(self, indexes):
        # is it multiple indexes?
        if isinstance(indexes, tuple):
            raise NotImplementedError("get item is not implemented for 2D indexing")
            # time_ind = indexes[0]
            # particle_index = indexes[1]
            # row_ids = self._particle_ids[self._start_indexes[time_ind] : self._start_indexes[time_ind + 1]]
            
        else:
            if isinstance(indexes, slice):
                raise NotImplementedError("indexing by slice not implimented yet")
            try:
                ind = indexes.__index__()
            except AttributeError:
                # not a simple index
                raise TypeError(f"indices must be integers or slices, not {type(indexes)}")

            row = np.empty(self.shape[1], dtype=self.dtype)
            row[:] = self._FillValue
            data = self._data_array[self._start_indexes[ind] : self._start_indexes[ind+1]]
            pids = self._particle_ids[self._start_indexes[ind] : self._start_indexes[ind+1]]
            for pid, dat in zip(pids, data):
                row[self._id_row_index[pid]] = dat
            row_var = xr.Variable(dims=(self.dims[1],), data=row)

        return row_var

    @property
    def shape(self):
        return (len(self), np.diff(self._start_indexes).max())

    def __len__(self):
        return len(self._start_indexes) - 1



