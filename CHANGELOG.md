# Changelog

All notable changes to **ogs6py** will be documented in this file.

### Changes
* parse input if input is given (allows for execution of given file if no replace function is called)
* logparser can now output from staggered scheme
* OGS executables from a singularity container are now supported as well

## [0.32]

### Changes
* added some tests for replace method
* add logfile parsing capabilities for output produced by PETSc
* add replace mesh function
* add compose from CSV tool
* add file include finction to outsource xmldata

### Bugfixes
* media are also recogniced if the id attribute is missing
* fix in log parser to recognise times in scientific format

## [0.31]

### Changes
* ogs6py uses now PEP8 naming convention for all ogs6py methods (lowercase with underscore separation)

### Bugfixes

### Additions

