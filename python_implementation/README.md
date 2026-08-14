# nc_particles

Package for working with the nc_particles data format in netcdf:

https://noaa-orr-erd.github.io/nc_particles/nc_particle_standard.html

Include in this package are two implimentations:

* xarray-based implimentation:

(incomplete)

Provides a duck-typed xarray Dataset (and Variables) that "looks like" and "acts like" "regular" rectangular xarray objects.

* Pure netcdf4 base implementation

Provides `Reader` and `Writer` classes that help read and write nc_particles files -- with a custom interace, and pute netCDF4 libary -- returning and consuming numpy arrays of data.

## xarray base implementation

THe goal of the nc_particles xarray implimentation is to provide an xarray-like object for nc_particles files.

### Reading nc_particles files with xarray:

```
In [65]: from nc_particles import Particles
In [66]: particles = Particles.from_file('boston_trajectory.nc')

# See what's in there
In [69]: [*particles]
Out[69]: ['spill_num', 'longitude', 'age', 'depth', 'mass', 'latitude', 'status_codes']
```

See the time series -- 25 timesteps:
```
In [80]: particles.time.shape
Out[80]: (25,)

<xarray.DataArray 'time' (time: 25)> Size: 200B
array(['2013-03-12T10:00:00.000000000',
       '2013-03-12T10:30:00.000000000',
       ...
       '2013-03-12T21:30:00.000000000',
       '2013-03-12T22:00:00.000000000'], dtype='datetime64[ns]')
```

You can get at individual variables, like xarray:

```
In [82]: particles['latitude'].shape
Out[82]: (25, 100)

# it "looks" like a 25X100 rectangular array
# 25 timesteps by 100 particles
```
When indexed, the variable-length arrays are returned

```
In [88]: particles['latitude'][0]
Out[88]: 
<xarray.DataArray 'latitude' (data: 5)> Size: 40B
[5 values with dtype=float64]
Dimensions without coordinates: data
Attributes:
    units:          degrees_north
    long_name:      latitude of the particle
    standard_name:  latitude

In [89]: particles['latitude'][24]
Out[89]: 
<xarray.DataArray 'latitude' (data: 100)> Size: 800B
[100 values with dtype=float64]
Dimensions without coordinates: data
Attributes:
    units:          degrees_north
    long_name:      latitude of the particle
    standard_name:  latitude
```





## Classic implementation

### Reading nc_particles files:

(see the example notebook)

Opening a file:

```
In [1]: from nc_particles import Reader

In [2]: # Open a file

In [3]: particles = Reader("boston_trajectory.nc")

In [4]: # see what data are there

In [5]: print(particles.variables)
['spill_num', 'longitude', 'age', 'depth', 'mass', 'latitude', 'status_codes', 'id']

```

Extracting data:

```
# What are the timesteps in the data?

# how many timesteps?

In [8]: len(particles.times)
Out[8]: 25

# What are they?

In [7]: particles.times
Out[7]: 
masked_array(data=[cftime.DatetimeGregorian(2013, 3, 12, 10, 0, 0, 0, has_year_zero=False),
                   cftime.DatetimeGregorian(2013, 3, 12, 10, 30, 0, 0, has_year_zero=False),

                   ...

                   cftime.DatetimeGregorian(2013, 3, 12, 22, 0, 0, 0, has_year_zero=False)],

# To get the data from one timestep:
#  default: latitude and longitude

In [11]: positions = particles.get_timestep(24)

returns a dict, with the keys being the individual data:

In [12]: positions.keys()
Out[12]: dict_keys(['latitude', 'longitude'])

In [16]: positions['latitude'][:4]
Out[16]: 
masked_array(data=[42.41844903, 42.41192209, 42.41089803, 42.40928374],
             mask=False,
       fill_value=1e+20)

In [17]: positions['longitude'][:4]
Out[17]: 
masked_array(data=[-70.93185012, -70.92959493, -70.9425698 , -70.91475103],
             mask=False,
       fill_value=1e+20)

```

Specify which data you want

```

In [23]: data = particles.get_timestep(22, ['latitude', 'longitude', 'latitude', 'age', 'mass'])

In [24]: data.keys()
Out[24]: dict_keys(['latitude', 'longitude', 'age', 'mass'])

In [25]: data['mass'].shape
Out[25]: (95,)

```

```
In [34]: all_timesteps = particles.get_all_timesteps(variables=['latitude', 'longitude', 'mass'])

In [35]: all_timesteps.keys()
Out[35]: dict_keys(['latitude', 'longitude', 'mass'])
```

Values are lists of arrays -- each timestep in one array.

NOTE: each timestep may have a different number of particles, so it can't be returned as a 2D array.

```
In [38]: all_timesteps['latitude'][0].shape
Out[38]: (5,)

In [39]: all_timesteps['latitude'][20].shape
Out[39]: (87,)
```

Getting the attributes of a variable:

```
In [42]: particles.get_attributes('status_codes')
Out[42]: 
{'flag_meanings': '0: not_released, 2: in_water, 3: on_land, 7: off_maps, 10: evaporated, 12: to_be_removed,',
 'long_name': 'particle status code',
 'flag_values': '7 12 0 10 2 3'}
```

You can get the trajectory of an individual particle by specifying its particle ID:

```
In [50]: traj = particles.get_individual_trajectory(3)

In [51]: traj.keys()
Out[51]: dict_keys(['latitude', 'longitude'])
```

Units of a variable:

```
In [53]: particles.get_units('mass')
Out[53]: 'kilograms'
```

### Writing nc_particles files:

See `build_example.py` in the examples.

Create a Writer:

```
writter = nc_particles.Writer("example.nc",
              num_timesteps=3, # must specify if netcdf3
              # ref time for the time variable
              reference_time=datetime.datetime(2010, 11, 1, 0),
              nc_version=3  # 4 is the default.
              )
```
The number of timesteps need to be specified if using netCDF3 -- netCDF4 supports dynamic sizing.

The data can be written one timestep at a time -- all variables at once for that timestep:

```
        data = {}
        data['longitude'] = longitudes
        data['latitude'] = latitudes
        data['depth'] = depths
        data['mass'] = mass
        data['id'] = ids

        nc_file.write_timestep(a_datetime, data)
```
after writing -- file can be closed

```
nc_file.close()
```


