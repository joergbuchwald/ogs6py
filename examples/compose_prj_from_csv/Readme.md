# Compose OGS input file (prj) from a parameter table (csv)

In a frequent use case there are 2D-slices from a 3D-model.
The number of soil layers (materials) depends on the slice (position, orientation).
This scripts enables automatic processing, i.e. OGS simulations for a sequence of slices, by generating input files (prj) from templates.
The material data to be filled into the templates are read from a table (csv) that comes with the 3D-model.
