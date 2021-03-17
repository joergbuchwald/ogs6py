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

## 3. Log-Parser
To parse the output that is piped into a file named `out.log` you can simply do:


```python
df = model.parseOut("out.log")
```


```python
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>execution_time</th>
      <th>time_step/number</th>
      <th>time_step/t</th>
      <th>time_step/dt</th>
      <th>time_step/cpu_time</th>
      <th>time_step/output_time</th>
      <th>time_step/iteration/number</th>
      <th>time_step/iteration/assembly_time</th>
      <th>time_step/iteration/dirichlet_bc_time</th>
      <th>time_step/iteration/linear_solver_time</th>
      <th>time_step/iteration/cpu_time</th>
      <th>time_step/iteration/component_convergence/number</th>
      <th>time_step/iteration/component_convergence/dx</th>
      <th>time_step/iteration/component_convergence/x</th>
      <th>time_step/iteration/component_convergence/dx_relative</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>None</td>
      <td>0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.309836</td>
      <td>0.037808</td>
      <td>1</td>
      <td>0.074155</td>
      <td>0.004871</td>
      <td>0.101103</td>
      <td>0.183431</td>
      <td>0</td>
      <td>1.055600e-01</td>
      <td>2.448300e+04</td>
      <td>4.311400e-06</td>
    </tr>
    <tr>
      <th>1</th>
      <td>None</td>
      <td>0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.309836</td>
      <td>0.037808</td>
      <td>1</td>
      <td>0.074155</td>
      <td>0.004871</td>
      <td>0.101103</td>
      <td>0.183431</td>
      <td>1</td>
      <td>9.003300e+04</td>
      <td>5.112200e+09</td>
      <td>1.761100e-05</td>
    </tr>
    <tr>
      <th>2</th>
      <td>None</td>
      <td>0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.309836</td>
      <td>0.037808</td>
      <td>2</td>
      <td>0.066655</td>
      <td>0.003866</td>
      <td>0.076766</td>
      <td>0.150649</td>
      <td>0</td>
      <td>1.793800e-09</td>
      <td>2.448300e+04</td>
      <td>7.327000e-14</td>
    </tr>
    <tr>
      <th>3</th>
      <td>None</td>
      <td>0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.309836</td>
      <td>0.037808</td>
      <td>2</td>
      <td>0.066655</td>
      <td>0.003866</td>
      <td>0.076766</td>
      <td>0.150649</td>
      <td>1</td>
      <td>1.354300e+02</td>
      <td>5.112200e+09</td>
      <td>2.649100e-08</td>
    </tr>
    <tr>
      <th>4</th>
      <td>None</td>
      <td>0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.309836</td>
      <td>0.037808</td>
      <td>1</td>
      <td>0.065019</td>
      <td>0.003825</td>
      <td>0.074051</td>
      <td>0.146153</td>
      <td>0</td>
      <td>1.007800e-01</td>
      <td>2.448300e+04</td>
      <td>4.116300e-06</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1105</th>
      <td>None</td>
      <td>133</td>
      <td>12476400.0</td>
      <td>226448.0</td>
      <td>0.639850</td>
      <td>0.042357</td>
      <td>2</td>
      <td>0.066762</td>
      <td>0.003108</td>
      <td>0.079635</td>
      <td>0.152886</td>
      <td>1</td>
      <td>2.171600e+06</td>
      <td>6.487700e+09</td>
      <td>3.347300e-04</td>
    </tr>
    <tr>
      <th>1106</th>
      <td>None</td>
      <td>133</td>
      <td>12476400.0</td>
      <td>226448.0</td>
      <td>0.639850</td>
      <td>0.042357</td>
      <td>3</td>
      <td>0.068605</td>
      <td>0.003232</td>
      <td>0.080462</td>
      <td>0.155698</td>
      <td>0</td>
      <td>3.006000e-02</td>
      <td>2.672600e+04</td>
      <td>1.124700e-06</td>
    </tr>
    <tr>
      <th>1107</th>
      <td>None</td>
      <td>133</td>
      <td>12476400.0</td>
      <td>226448.0</td>
      <td>0.639850</td>
      <td>0.042357</td>
      <td>3</td>
      <td>0.068605</td>
      <td>0.003232</td>
      <td>0.080462</td>
      <td>0.155698</td>
      <td>1</td>
      <td>1.116500e+05</td>
      <td>6.487600e+09</td>
      <td>1.721000e-05</td>
    </tr>
    <tr>
      <th>1108</th>
      <td>None</td>
      <td>133</td>
      <td>12476400.0</td>
      <td>226448.0</td>
      <td>0.639850</td>
      <td>0.042357</td>
      <td>4</td>
      <td>0.069614</td>
      <td>0.003289</td>
      <td>0.080768</td>
      <td>0.157063</td>
      <td>0</td>
      <td>2.538300e-03</td>
      <td>2.672600e+04</td>
      <td>9.497500e-08</td>
    </tr>
    <tr>
      <th>1109</th>
      <td>None</td>
      <td>133</td>
      <td>12476400.0</td>
      <td>226448.0</td>
      <td>0.639850</td>
      <td>0.042357</td>
      <td>4</td>
      <td>0.069614</td>
      <td>0.003289</td>
      <td>0.080768</td>
      <td>0.157063</td>
      <td>1</td>
      <td>6.094500e+03</td>
      <td>6.487600e+09</td>
      <td>9.394000e-07</td>
    </tr>
  </tbody>
</table>
<p>1110 rows × 15 columns</p>
</div>


