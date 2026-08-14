"""
Code to make a trajectory file as simple rectangular arrays
from scratch

Used to confirm how it should look for the make_rect method
"""
from datetime import timedelta
import numpy as np
import xarray as xr 
import pandas as pd

# for a 10 timestep, 20 particle trajectory:

Nt = 10
Np = 20

time = pd.date_range("2000-01-01", periods=Nt, freq=timedelta(minutes=15))
lat = np.random.random((Nt, Np)) + 30.3
lon = np.random.random((Nt, Np)) * 2 - 78
depth = np.random.random((Nt, Np)) * 100
mass = np.random.random((Nt, Np)) * 0.001

part_id = np.arange(Np, dtype=np.uint16)


# set up the coords:
lat_arr = xr.DataArray(
    lat,
    coords={
        "time": time,
        "particles": part_id,
    },
    dims=["time", "particles"],
)

ds = xr.Dataset(
    {
        "lat": (["time", "num_particles"], lat, {"units": "degrees_north"}),
        "lon": (["time", "num_particles"], lon, {"units": "degrees_east"}),
        "depth": (["time", "num_particles"], depth, {"units": "m"}),
        "mass": (["time", "num_particles"], mass, {"units": "kg"}),
    },
    coords={
        "time": (["time"], time),
        "particle_ids": (["num_particles"], part_id),
    },
)

# buiiding it up piece by piece:

attrs = {"a global attribute": "a value",
             "another one": "something useless"}
vars = 


