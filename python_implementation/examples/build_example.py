#!/usr/bin/env python

"""
A script to build a little example netcdf file for the nc_particles format

This also serves as an example of how to use the Writer code.
"""

import numpy as np
import datetime
import nc_particles
import netCDF4

# create the data

# three timesteps in this case
timesteps = [datetime.datetime(2010, 11, 3, 12, 0),
             datetime.datetime(2010, 11, 3, 12, 30),
             datetime.datetime(2010, 11, 3, 13, 0),
             ]


# All the data, in a list.
# for a model run, this would be generated during the run.
all_data = [# three elements the first timestep
            {'time' : datetime.datetime(2010, 11, 3, 12, 0),
             'positions': np.array([(-88.0, 28.0, 0.0),
                                    (-88.1, 28.0, 0.1),
                                    (-88.1, 28.1, 0.2),
                                    ]),
             'mass': [0.1, 0.05, 0.07],
             'id': np.array([10, 5, 20], dtype=np.int32),
             },
             # four elements the second time step
             {'time' : datetime.datetime(2010, 11, 3, 12, 30),
             'positions': np.array([(-88.0, 28.0, 0.0),
                                    (-88.2, 28.05, 0.1),
                                    (-88.1, 28.1, 0.2),
                                    (-87.9, 27.9, 0.1),
                                    ]),
             'mass': [0.1, 0.05, 0.07, 0.06],
             'id': np.array([10, 5, 20, 13], dtype=np.int32),
             },
             # two elements the third time step
             {'time' : datetime.datetime(2010, 11, 3, 13, 0),
             'positions': np.array([(-88.3, 28.1, 0.0),
                                    (-88.1, 28.0, 0.1),
                                    ]),
             'mass': [0.05, 0.06],
             'id': np.array([10, 20], dtype=np.int32),
             },
             ]

def build_nc_part_file(filename):

    ## create the nc file writer
    nc_file = nc_particles.Writer("example.nc",
                                  num_timesteps=3, # must specify if netcdf3
                                  ref_time=datetime.datetime(2010, 11, 1, 0) # ref time for the time variable
                                  )

    for timestep in all_data:
        # set the data:
        data = {}
        data['longitude'] = timestep['positions'][:,0]
        data['latitude'] = timestep['positions'][:,1]
        data['depth'] = timestep['positions'][:,2]
        data['mass'] = timestep['mass']
        data['id'] = timestep['id']
        nc_file.write_timestep(timestep['time'], data)

    nc_file.close()


def build_rect_file(filename):
    with netCDF4.Dataset(filename, mode='w') as ncds:
        ncds.createDimension('time', size=3)
        ncds.createDimension('particle_id', size=4)
        time = ncds.createVariable('time', datatype=np.uint32, dimensions=('time'))
        time_units = "seconds since 2010-01-01T00:00:00"
        time[:] = netCDF4.date2num(timesteps, units=time_units, calendar='standard')
        time.units = time_units
        names = ['longitude',
                 'latitude',
                 'depth',
                 'mass']

        for name in names:
            ncds.createVariable(name,
                                datatype=np.float64,
                                dimensions=('time', 'particle_id'),
                                fill_value=np.nan)

        for i, timestep in enumerate(all_data):
            for id in timestep['id']:
                for pos, mass in zip(timestep['positions'], timestep['mass']):
                    ncds.variables['longitude'][i, id] = pos[0]
                    ncds.variables['latitude'][i, id] = pos[1]
                    ncds.variables['depth'][i, id] = pos[2]
                    ncds.variables['mass'][i, id] = mass

        part_id = ncds.createVariable('particle_id',
                                      datatype=np.uint32,
                                      dimensions=('particle_id'))
        part_id[:] = range(4)

if __name__ == "__main__":
    build_nc_part_file("example.nc")
    build_rect_file("rect_example.nc")
