# Draft Proposal for a netcdf standard for storing/sharing data from particle tracking models.

Version: 0.1.0

Authors: (please add yourself here ... )

Chris Barker: NOAA Emergency Response Division: Chris.Barker@noaa.gov



## Motivation:

Particularly after the DeepWater Horizon Oil Spill incident, there has been an increase in interest and model development for oil spill models. Most oil spill models are fundamentally particle tracking models.  In order to simplify communication and data exchange, a standard for the output for such models is needed.  The netcdf CF metadata standard (http://cfconventions.org/) has been very successful for facilitating data exchange among climate modelers, and has been expanded to support, and been widely adopted by, the atmospheric and oceanographic modeling community, as well as field data storage and sharing.

However, the CF standard does not currently include an appropriate standard for the trajectories of collections of particles as output by particle tracking models.  Thus we propose to introduce a new standard data format for particle tracking results that builds on the CF standard, maintaining compatibility wherever possible.

While the original motivation (and background of most of the participants) was to support oil spill transport models, we hope that the standard will accommodate other particle tracking models: larval transport, atmospheric dispersion, etc.

## History:

Discussion of this standard began informally via email and some discussion on the cf-metadata mailing list (http://mailman.cgd.ucar.edu/mailman/listinfo/cf-metadata), involving people from NOAA, SINTEF, Unidata, USGS, and ASA

## NetCDF Version

So far, the intent is to conform to the NetcCDF version 3 ("classic") data model. This still allows the use of netcdf4, which can allow compression, etc, but there are still software tools that only supports version 3. However, there are some features of version 4 that may be helpful for this use-case, so it should be considered -- details in the technical section of this doc.

## Goals

Some of the goals of the standard: what we are trying to accommodate:

In general, particle tracking models use large numbers of particles, moving them in space, over time. Most often, the properties of the collection of particles is of interest, rather than the path of any individual particle.  Some models create and destroy particles during the model run, and often it is unknown how many particles will ultimately be created at the beginning of the run (or when the output file may be begun to be written). Particles can have a number of data fields associated with them.

Particles may have positions in either 2 or 3 dimensions (plus time, of course).

We've decided that it is more common to ask the question: "Where are all the particles at a given time", than "How did a particular particle's position change with time?". Which of these questions is generally asked controls the likely data access patterns, which, in turn, control the optimum layout of the data.


## Data Arrangement:

The biggest question is how to put the data associated with the particles into netcdf arrays. Each particle has a number of values associated with it, with the values changing with time -- at least x and y, maybe z, and generally a number of other properties: mass, diameter, etc. For a constant number of particles, the obvious choice is a (num_times, num_particles) 2-d array, with the time axis unlimited. However, with a model that creates and destroys particles during a run, there is no constant num_particles value to use. One might allocate a as-large-as-might-be-needed array, and have a lot of empty space, but this would:

a) waste a lot of space in the file and
b) not be possible if it is unknown how many particles will ultimately be used at the beginning of the run.

While compression could help mitigate (a), full flexibility to support creation and removal of particles requires a "ragged array" format.

A ragged array can be thought of as a 2-d array, where the length of each row is arbitrary. In this case, there is one row for each time step, and each row is long enough to accommodate the number of particles at that time.

NetCDF does not have a built-in ragged array representation. However, the CF standard defines one for  time series data at discrete points. (http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_contiguous_ragged_array_representation). We propose a similar approach to ragged arrays for particle trajectories.

The data in a ragged array are stored lined up end to end in a single 1-D array. Each "row" is then a piece of that 1-d array. There are (at least) two methods to define the rows: either specify the length of each row, or specify the index to the beginning of each row.  The current CF standard ragged arrays specify the length of each row, so that convention is followed here as well.

Note that with netcdf4, ragged arrays can be handled in perhaps a more natural (or at least built-in) way: (http://www.unidata.ucar.edu/software/netcdf/workshops/2010/netcdf4/VarLens.html). At the moment, we still want to support NetCDF3, so this is not an option.

Another challenge is that netcdf3 only allows one unlimited dimension, so if you don't know the number of particles, than you need to know the number of time steps when you start to write the file.  The data array is length `num_timesteps * sum_over_time_(num_particles_per_timestep)`, which gives the unlimited dimension of data -- but we also need the time dimension for storing the particle count per row.

One solution, if you don't know a priori the run-time of the model, is to simply use a "as_big_as_it_might_get" time dimension -- it wouldn't waste much space, and you could re-write the file later to clean it up.

Netcdf4 would allow the time dimension to be unlimited as well, without any change to this standard.



## The Standard

### Dimensions: 

Required dimensions are:

```
dimensions:
	time = 289 ;
	data = UNLIMITED ; // (3832 currently)
```

`time` is the standard CF time dimension. `data` is the dimension for the flattened ragged array.

### Variables: 

Required variables are:

```
variables:
	double time(time) ;
		time:units = "seconds since 2010-01-24 00:00:00" ;
		time:long_name = "time" ;
		time:standard_name = "time" ;
		time:calendar = "gregorian" ;
	int particle_count(time) ;
		particle_count:units = "1" ;
		particle_count:long_name = "number of particles in a given timestep" ;
		particle_count:ragged_row_count = "particle count at nth timestep" ;
	float longitude(data) ;
		longitude:standard_name = "longitude" ;
		longitude:long_name = "longitude of the particle" ;
		longitude:units = "degrees_east" ;
	float latitude(data) ;
		longitude:standard_name = "latitude" ;
		latitude:long_name = "latitude of the particle" ;
		latitude:units = "degrees_north" ;
```

`time`, `longitude`, and `latitude` have their standard CF meanings. (longitude and latitude could be x and y, depending on the projection).  

`particle_count` provides the data for the ragged array. It is a 1-d array with dimension of time. It specifies how many particles there are at each time step. 

QUESTION: should the particle_count variable have the `sample_dimension` attribute as used in the ragged array representation for discrete sampling geometries (http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#representations-features): 

Any other data associated with the particles would be stored in arrays of the `data` dimension. For example:

```
	float depth(data) ;
		depth:long_name = "particle depth below sea surface" ;
		depth:units = "meters" ;
		depth:axis = "z positive down" ;
	float mass(data) ;
		mass:units = "grams" ;
	int age(data) ;
		age:description = "from age at time of release" ;
		age:units = "seconds" ;
```

Global attributes would be specified the same as other CF-compliant files.

### Particle ID:

It is often desired to keep track of which particle is which over time. In this case, a particle ID variable can be defined:

	int id(data) ;
		id:description = "particle ID" ;
		id:standard_name = "particle_id_number";

The same particle will carry the same ID for all time. If particles are created and destroyed, this allows the client software to track particular particles, as they will not be at the same index in a row for all time.

### Data associated with particles that is NOT time varying:

There may be data associated with particles that is not time varying. In this case, you might want to map the data to particle ID, rather than repeating it at each time step. This would require a new dimension:

```
dimensions:
      ... 
num_particles = 3000 ; // This may not be known at the start of the run
...
```

If that value is not known when the model run starts, one could use a larger-than-it-needs-to-be value, or, with netcdf4, use UNLIMITED. Then one could provide a mapping from particle ID to data. NOTE: this could create a complication with data types -- particle ID will be an integer, if you want to map a non-integer value to the particle ID, you'd need another intermediate array -- one to map particle ID to index into the data array, one to provide the data.

QUESTION: Does netCDF4 support mixed data types in an array? If so, does OpenDAP?

## Small Example:

The following is a micro example of the CDL for a particle file netcdf File.

```
netcdf test_particles {
dimensions:
	time = 3 ;
	data = UNLIMITED ; // (9 currently)
variables:
	int time(time) ;
		time:units = "seconds since 2010-11-03T12:00:00" ;
		time:comment = "unspecified time zone" ;
		time:long_name = "time since the beginning of the simulation" ;
		time:standard_name = "time" ;
		time:calendar = "gregorian" ;
	int particle_count(time) ;
		particle_count:units = "1" ;
		particle_count:long_name = "number of particles in a given timestep" ;
		particle_count:ragged_row_count = "particle count at nth timestep" ;
	double lat(data) ;
		lat:units = "degrees_north" ;
		lat:long_name = "latitude of the particle" ;
		lat:standard_name = "latitude" ;
	double mass(data) ;
		mass:units = "grams" ;
		mass:long_name = "mass of particle" ;
	double depth(data) ;
		depth:units = "meters" ;
		depth:long_name = "particle depth below sea surface" ;
		depth:standard_name = "depth" ;
		depth:axis = "z positive down" ;
	double lon(data) ;
		lon:units = "degrees_east" ;
		lon:long_name = "longitude of the particle" ;
		lon:standard_name = "longitude" ;
	int id(data) ;
		id:long_name = "particle ID" ;

// global attributes:
		:comment = "Some simple test data" ;
		:source = "example data from nc_particles" ;
		:references = "" ;
		:title = "Sample data/file for particle trajectory format" ;
		:CF\:featureType = "particle_trajectory" ;
		:history = "Evolved with discussion on CF-metadata listserve" ;
		:institution = "NOAA Emergency Response Division" ;
		:conventions = "CF-1.6" ;
data:

 time = 0, 1800, 3600 ;

 particle_count = 3, 4, 2 ;

 lat = 28, 28, 28.1, 28, 28, 28.1, 27.9, 28, 28 ;

 mass = 0.01, 0.005, 0.007, 0.01, 0.005, 0.007, 0.006, 0.01, 0.005 ;

 depth = 0, 0.1, 0.2, 0, 0.1, 0.2, 0.1, 0, 0.1 ;

 lon = -88, -88.1, -88.1, -88, -88.1, -88.1, -87.9, -88, -88.1 ;

 id = 0, 1, 2, 0, 1, 2, 3, 1, 3 ;
}
```



## Optimizations:

The flexibility offered by this proposal comes at the cost of addition complexity in client software. This required more code, and loss of performance, compared to a simple 2-d (time, num_particles) array approach. However, in cases where the data really are simple, it is fairly easy to identify (i.e. every value in the `particle_count` variable is the same) that the "ragged array" is not really ragged, and an optimized (and simpler) code path could be followed.

Another option would be to have two "versions" of the standard, one ragged, and one not, with an attribute specifying which it was. I’d rather not do that though; we’d end up with a lot of client software that only worked with one or the other.


## Standard Names:

Standard names already defined by the CF standard will be used were possible. This included obvious ones like longitude, latitude, depth, etc. and wherever possible, physical properties associated with a particle. We expect that a number of new standard names will need to be coined to support oil spill modeling applications. Other particle tracking applications may develop their own standard name tables.

A very small list is begun here:


| Standard name	        | Canonical Units |  Description
|-----------------------|-----------------|--------------
| particle_mass	        | g (kg?)	  | Total mass of particle
| particle_age	        | seconds	  | 
| droplet_diameter      | meters          | diameter of oil droplets (or gas bubbles?)		

### Oil components

Each oil spill model has its own way of describing the composition of the oil, and many track individual components or "pseudo components". Thus, it may not be possible to standardize these names, etc, but it would be good to perhaps capture the state of the practice here and see what shakes out.

## API

As this data format requires not entirely trivial data processing to read and write, this proposal is accompanied by a Python package that provides services to read and write the format. It might be good to standardize that API, so the people that need to read and write the format with other packages and different programming languages can communicate with each other.

the nc_particles python package will serve as a reference implementation.

### Core API:

The core API is to have a class or data structure that contains the actual data (maybe in memory, or maybe virtually) following the data model encompassed by this standard. 

This class will have methods (associated functions in a non-OO language) to query that data and access subsets of it in standard ways. 










