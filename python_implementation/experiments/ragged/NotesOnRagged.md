# Notes on using the awkward based ragged array with xarray:
(and for my use case)

ragged: https://github.com/ChrisBarker-NOAA/ragged/

## My use case:

Storing (and working with) the results of particle tracking models:

Particle tracking models store data associated with particles that are moving in space (and may be changing other properties) over time.

In the simplest case, the data can be stored in a (time, particle_id) 2D array.

However, some model create and destroy particles as the model runs -- so for each timestep the can be a different number of particles -- hence the ragged array.

A draft netcdf standard has been defined here:

https://noaa-orr-erd.github.io/nc_particles/nc_particle_standard.html

We are currently working on refining the standard, and writing modern, xarray-based code to work with the data.

### Code is here:

https://github.com/NOAA-ORR-ERD/nc_particles/tree/new_code/python_implementation

(xarray-based code in nc_particles.particles)

The idea behind that code is to wrap xarray variables, rather than use a ragged array as a duck array. That allows the native xarray saving and load from files (e.g. netcdf) to be automatic and transparent, and allows users to get a "regular" xarray VAriable out when indexing into the data.

### structure:

The data itself is stored in a 1-D array -- with meta-data defining the length of the rows, particle IDs, etc, to access the subset of the data that folks need.

This is the same (almost) structure used in the netcdf format (which follows the CF standard for ragged arrays)

## Using `ragged`

A quick test of using ragged as a duck-array under the hood revealed some issues:

1) shape: The `ragged.array` class exposes a shape with None for the ragged dimension(s):
```
In [4]: ra
Out[4]:
ragged.array([
    [1, 2, 3, 4],
    [5, 6],
    [7, 8, 9, 10, 11],
    [12, 13, 14]
])

In [5]: ra.shape
Out[5]: (4, None)
```
This makes some sense, as the ragged dimension is variable, and thus undefined.

Howver, that does not make xarray happy:

```
In [6]: xr.DataArray(ra)
Out[6]: ---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
...
File ~/miniforge3/envs/ragged/lib/python3.12/site-packages/xarray/namedarray/core.py:429, in NamedArray.size(self)
    418 @property
    419 def size(self) -> _IntOrUnknown:
    420     """
    421     Number of elements in the array.
    422
   (...)
    427     numpy.ndarray.size
    428     """
--> 429     return math.prod(self.shape)

TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
```
xarray very much expects the shape to a a tuple of integers.

NOTE: apparetnly the None in shape does conform to the array interface -- but not xarray -- but what *should* xarray do with this?

One option (and what I've done with my implementation) is to think of a ragged array as a special case of a sparse array -- to it's shape would be: `(num_rows, longest_row)`

2) When iterating over a ragged array, you get 2-d ragged arrays:
```
In [12]: for row in ra:
    ...:     print(type(row))
    ...:     print(row.shape)
    ...:     print(row)
    ...:
<class 'ragged._spec_array_object.array'>
(4, None)
[
    1,
    2,
    3,
    4
]
<class 'ragged._spec_array_object.array'>
(2, None)
[
    5,
    6
]
<class 'ragged._spec_array_object.array'>
(5, None)
[
    7,
    8,
    9,
    10,
    11
]
<class 'ragged._spec_array_object.array'>
(3, None)
[
    12,
    13,
    14
]
```

This may be a bug (misfeature?) -- as indexing does what I'd expect:
```
In [13]: ra[2]
Out[13]: ragged.array([7, 8, 9, 10, 11])

In [14]: ra[2].shape
Out[14]: (5,)
```
I *think* iterating and indexing is supposed to result in the same thing.










