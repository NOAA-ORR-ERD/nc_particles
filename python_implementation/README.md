# nc_particles

Package for working with the nc_particles data format in netcdf:

https://noaa-orr-erd.github.io/nc_particles/nc_particle_standard.html

Include in this pacakge are two implimentations:

* xarray-based implimentation:

(incomplete)

Provides a duck-typed xarray dataset (and variables) that "looks like" and "acts like" an "regular" rectangules xarray objects.

* Pure netcdf4 base implementation

Provides `Reader` and `Writer` classes that help jread and write nc_particles files -- with a custom interace, and pute netCDF4 libary -- returning numpy arrays of data.

## xarray base implimentation

## Classic implementation

### Reading nc_particles files:

(see the example notebook)

Opening a file:

```
from nc_particles import Reader

particles = Reader("r = nc_particles.Reader('boston_trajectory.nc')")

# what data is in there?
# all the data associated with the particles can be listed:
print(r.variables)

```

Extracting data:

```
# What are the timesteps in the data?

print(r.times)

# To get the data from one timestep:

positions = r.get_timestep(24)

returns a dict, with the keys being the individual data:

e.g.: latitude, longitude

```




