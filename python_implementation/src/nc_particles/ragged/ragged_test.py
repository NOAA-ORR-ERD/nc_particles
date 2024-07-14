"""
test to see what can be done with ragged
"""
import numpy as np
import xarray as xr
import ragged

data = [[1, 2, 3, 4],
        [5, 6],
        [7, 8, 9, 10, 11],
        [12, 13, 14],
        ]

ra = ragged.array(data, dtype=np.float64)

# Iterating through the rows:
print("Iterating through the rows:")
for row in ra:
   print(type(row))
   print(row.shape)
   print(row)

# Convert to numpy array
# no __array__ property
# npa = ra.__array__
npa = ragged.asarray(ra)
print(npa)




