# ogs6py

ogs6py is a python-API for the OpenGeoSys finite element sofware.
Its main functionalities include creating and altering OGS6 input files as well as executing OGS.
The package allows to streamline OGS-workflows with python or Julia entirely in jupyter or pluto notebooks as demonstrated in the following video:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/eihNKjK-I-s/0.jpg)](https://www.youtube.com/watch?v=eihNKjK-I-s)


To alter and execute OGS input, e.g., for looping over parameter ranges, two approaches exist: 

    1. creating a new input file using python method calls
    2. altering existing input files

### 1. Creating a new input file
 
The following example consists of a simle mechanics problem. The names of the method calls are based on the corresponing XML tags. The `MKL=True` option executes `source /opt/intel/mkl/bin/mklvars.sh intel64` before the ogs call.


```python
from ogs import *

model = OGS(PROJECT_FILE="simple_mechanics.prj", MKL=True)
model.geo.addGeom(filename="square_1x1.gml")
model.mesh.addMesh(filename="square_1x1_quad_1e2.vtu")
model.processes.setProcess(name="SD",
                           type="SMALL_DEFORMATION",
                           integration_order=2,
                           solid_density="rho_sr",
                           specific_body_force="0 0")
model.processes.setConstitutiveRelation(type="LinearElasticIsotropic",
                                        youngs_modulus="E",
                                        poissons_ratio="nu")
model.processes.addProcessVariable(process_variable="process_variable",
                                   process_variable_name="displacement")
model.processes.addProcessVariable(secondary_variable="sigma",
                                   output_name="sigma")
model.timeloop.addProcess(process="SD",
                          nonlinear_solver_name="basic_newton",
                          convergence_type="DeltaX",
                          norm_type="NORM2",
                          abstol=1e-15,
                          time_discretization="BackwardEuler")
model.timeloop.setStepping(process="SD", type="FixedTimeStepping",
                           t_initial=0,
                           t_end=1,
                           repeat=4,
                           delta_t=0.25)
model.timeloop.addOutput(type="VTK",
                         prefix="blubb",
                         repeat=1,
                         each_steps=10,
                         variables=["displacement", "sigma"])
model.parameters.addParameter(name="E", type="Constant", value=1)
model.parameters.addParameter(name="nu", type="Constant", value=0.3)
model.parameters.addParameter(name="rho_sr", type="Constant", value=1)
model.parameters.addParameter(name="displacement0",
                              type="Constant",
                              values="0 0")
model.parameters.addParameter(name="dirichlet0", type="Constant", value=0)
model.parameters.addParameter(name="dirichlet1", type="Constant", value=0.05)
model.processvars.setIC(process_variable_name="displacement",
                        components=2,
                        order=1,
                        initial_condition="displacement0")
model.processvars.addBC(process_variable_name="displacement",
                        geometrical_set="square_1x1_geometry",
                        geometry="left",
                        type="Dirichlet",
                        component=0,
                        parameter="dirichlet0")
model.processvars.addBC(process_variable_name="displacement",
                        geometrical_set="square_1x1_geometry",
                        geometry="bottom",
                        type="Dirichlet",
                        component=1,
                        parameter="dirichlet0")
model.processvars.addBC(process_variable_name="displacement",
                        geometrical_set="square_1x1_geometry",
                        geometry="top",
                        type="Dirichlet",
                        component=1,
                        parameter="dirichlet1")
model.nonlinsolvers.addNonlinSolver(name="basic_newton",
                                    type="Newton",
                                    max_iter=4,
                                    linear_solver="general_linear_solver")
model.linsolvers.addLinSolver(name="general_linear_solver",
                              kind="lis",
                              solver_type="cg",
                              precon_type="jacobi",
                              max_iteration_step=10000,
                              error_tolerance=1e-16)
model.linsolvers.addLinSolver(name="general_linear_solver",
                              kind="eigen",
                              solver_type="CG",
                              precon_type="DIAGONAL",
                              max_iteration_step=10000,
                              error_tolerance=1e-16)
model.linsolvers.addLinSolver(name="general_linear_solver",
                              kind="petsc",
                              solver_type="cg",
                              precon_type="bjacobi",
                              max_iteration_step=10000,
                              error_tolerance=1e-16)
model.writeInput()
```




    True




```python
model.runModel(path="~/github/ogs/build_mkl/bin")
```

    OGS finished


An example using the MPL can be find in example_THM.py.

### 2. Alternatively it is possible to alter existing files using the available replace methods:

E.g., to iterate over three Young's moduli one can use the replace parameter method:


```python
Es = [1,2,3]
filename = "simple_mechanics.prj"
for E in Es:
    model = OGS(INPUT_FILE=filename, PROJECT_FILE=filename, MKL=True)
    model.replaceParameter(name="E", value=E)
    model.replaceTxt("out_E="+str(E), xpath="./time_loop/output/prefix")
    model.writeInput()
    model.runModel(path="~/github/ogs/build_mkl/bin")
```

    OGS finished
    OGS finished
    OGS finished


Instead of the `replaceParameter` method, the more general `replaceTxt` method can be used


```python
model.replaceTxt(E, xpath="./parameters/parameter[name='E']/value")
```

The Young's modulus in this file can also be accessed through 0'th occurrence of the place addressed by the xpath `./parameters/parameter/value`


```python
model.replaceTxt(E, xpath="./parameters/parameter/value", occurrence=0)
```

For MPL based processes, there exist specific functions to set phase and medium properties: E.g.,


```python
model.replacePhaseProperty(mediumid=0, phase="Solid", name="thermal_expansivity", value="42")
```

for a phse property and


```python
model.replaceMediumProperty(mediumid=0, name="porosity", value="0.24")
```

for a property that lives on the medium level.


```python

```
