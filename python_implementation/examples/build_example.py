#!/usr/bin/env python

"""
A script to build a little example netcdf file for the nc_particles format
"""

import numpy as np
import datetime
import nc_particles

nc_file = nc_particles.Writer("sample.nc",
                              num_timesteps=3,
                              ref_time=datetime.datetime(2010, 11, 1, 0)
                              )




#start_time = datetime.datetime(2010, 11, 3, 12)
#timesteps = [T.start_time + datetime.timedelta(hour=1) for i in range(10)]
timesteps = [datetime.datetime(2010, 11, 3, 12, 0),
             datetime.datetime(2010, 11, 3, 12, 30),
             datetime.datetime(2010, 11, 3, 13, 0),
             ]

# empty data dict:
data = {'latitude':[],
        'longitude':[],
        'mass':[],
        'id':[],
        }
for dt in timesteps:
    nc_file.write_timestep(dt, data)





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