#!/usr/bin/env python

"""
A script to build a little example netcdf file for the nc_particles format

This also serves as an example of how to use the code.
"""

import numpy as np
import datetime
import nc_particles

## crate the nc file writer
nc_file = nc_particles.Writer("sample.nc",
                              num_timesteps=3, # must specify if netcdf3
                              ref_time=datetime.datetime(2010, 11, 1, 0) # ref time for the time variable
                              )

# three timesteps in this case
timesteps = [datetime.datetime(2010, 11, 3, 12, 0),
             datetime.datetime(2010, 11, 3, 12, 30),
             datetime.datetime(2010, 11, 3, 13, 0),
             ]


LEtype = np.dtype([("long","f8"), ("lat", "f8"), ("z", "f8"), ("mass","f8"), ("flag","u1"), ("id","i4")])

# All the data, in a list.
# for a model run, this would be generated during the run.
all_data = [# three elements the first timestep
            {'time' : datetime.datetime(2010, 11, 3, 12, 0),
             'positions': np.array([(-88.0, 28.0, 0.0),
                                    (-88.1, 28.0, 0.1),
                                    (-88.1, 28.1, 0.2),
                                    ]),
             'mass': [0.1, 0.05, 0.07],
             'id': np.array([0,1,2], dtype=np.int32),
             },
             # four elements the second time step
             {'time' : datetime.datetime(2010, 11, 3, 12, 30),
             'positions': np.array([(-88.0, 28.0, 0.0),
                                    (-88.1, 28.0, 0.1),
                                    (-88.1, 28.1, 0.2),
                                    (-87.9, 27.9, 0.1),
                                    ]),
             'mass': [0.1, 0.05, 0.07, 0.06],
             'id': np.array([0,1,2,3], dtype=np.int32),
             },
             # two elements the third time step
             {'time' : datetime.datetime(2010, 11, 3, 13, 0),
             'positions': np.array([(-88.0, 28.0, 0.0),
                                    (-88.1, 28.0, 0.1),
                                    ]),
             'mass': [0.05, 0.06],
             'id': np.array([1,3], dtype=np.int32),
             },
             ]


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





# Trajectory = []
# # first timestep
# Trajectory.append(np.array( [ (-88.0, 28.0, 0.0, .01,  2, 0),
#                               (-88.1, 28.0, 0.1, .005, 2, 1),
#                               (-88.1, 28.1, 0.2, .007, 2, 2),
#                               ], dtype=LEtype
#                             )
#                   )
# # second timestep
# Trajectory.append(np.array( [ (-88.0, 28.0, 0.0, .01,  2, 0),
#                               (-88.1, 28.0, 0.1, .005, 2, 1),
#                               (-88.1, 28.1, 0.2, .007, 2, 2),
#                               (-87.9, 27.9, 0.1, .006, 2, 3),
#                               ], dtype=LEtype
#                             )
#                   )
# # third timestep
# Trajectory.append(np.array( [ (-88.0, 28.0, 0.0, .01,  2, 1),
#                               (-88.1, 28.0, 0.1, .005, 2, 3),
#                               ], dtype=LEtype
#                             )
#                   )
                  


# num_LEs = [len(a) for a in Trajectory]
           
# print Trajectory
#                           