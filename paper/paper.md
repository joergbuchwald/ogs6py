---
title: 'ogs6py and VTUinterface: streamlining OpenGeoSys workflows in Python'
tags:
  - Python
  - physics
  - THMC
  - VTU
  - time-series
  - sensitivity analysis
  - uncertainty quantification

authors:
  - name: Jörg Buchwald^[corresponding author]
    orcid: 0000-0001-5174-3603
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Olaf Kolditz
    orcid: 0000-0002-8098-4905
    affiliation: "1, 3, 4"
  - name: Thomas Nagel
    orcid: 0000-0001-8459-4616
    affiliation: "2, 4"
affiliations:
 - name: Helmholtz Center for Environmental Research - UFZ, Leipzig, Germany
   index: 1
 - name: Technische Universität Bergakademie Freiberg, Germany
   index: 2
 - name: Technische Universität Dresden, Germany
   index: 3
 - name: TUBAF-UFZ Center for Environmental Geosciences, Germany
   index: 4
date: 12 May 2021
bibliography: paper.bib

---

# Summary

ogs6py is a Python interface for the OpenGeoSys finite element software [@Bilke2019].
In conjunction with VTUinterface it is possible to streamline modeling workflows
in Jupyter Notebooks using Python.
With this article, we wish to introduce two new Python modules that facilitate
the pre- and postprocessing of finite element calculations of OpenGeoSys and thus
make this code more accessible. Their use is demonstrated along workflows typically
encountered by the modeller, including the variationsof parameters, boundary conditions,
or solver settings, the verification of simulation results by comparison to analytical
solutions, the set-up and evaluation of ensemble runs, the analysis of results by line plots,
time series, or transient contour plots.

# Statement of need

Driven by its ease-of-use and flexibility as an open-source 
dynamic language, its vast modular ecosystem, the development of powerful plotting
libraries and the Jupyter Notebook technology, Python became the quasi-standard for 
scientific data analysis in the modelling community during the past decade.
However, the attractiveness of Phython is not just limited to postprocessing. 
E.g, with the Python wrapper for GMSH [@geuzaine2009gmsh] or the tool meshio [@] also pre-processing tasks can
be easily conducted without leaving the IPython command prompt. The useability of a modeling package
is therefore greatly enhanced if Python bindings are provided. In fact, 
while many open-source tools effectively forced the user to learn a singular syntax
for interacting with the software, Python bindings allow control over such tools from 
within the Python world and thus open them up for a wider community of users.

Here, we are particularly addressing the open-source code OpenGeoSys [@Bilke2019]. It is our aim
to facilitate both pre- and post-processing workflows using the Python ecosystem. 
This aim was not the least inspired by the desire to facilitate setting up, controlling and
evaluating ensemble runs [@Buchwald2020,@Chaudhry2021] but has now taken on a wider perspective of general 
software usability.

As standard output format, OpenGeoSys uses VTK unstructured grid files (VTU) as timeslices stacked together by a PVD file.
These can be analyzed typically using Paraview [@ahrens2005paraview]. For interactive Python use the Python 
wrapper for VTK [@schroeder2000visualizing] and some other tools like PyVista [@sullivan2019pyvista] or Mayavi [@ramachandran2011mayavi] 
are available facilitating an easier access to the VTK library.
While the direct use of the VTK library is quite cumbersome for quite _simple_ tasks, like reading data for a given point set, especially when interpolation between grid points is also required. The latter packages focus mainly on 3D visualization. However, the _bread and butter_ bussiness of a finite-element-modeller often cosists of the extraction of single- or multiple point time-series data.
To our knowledge the named packages (with the exception of Paraview) don't have file support for PVDs or time series data, yet ([@pvdissue; @timeseriesissue].

# Usage

With ogs6py it is possible to create complete OGS source files from scratch or to alter existing file.
The folloing example uses a complete input file for a coupled THM point heat source problem, exchanges parts and writes the input, runs the problem and analyses the results.


```python
from ogs6py.ogs import OGS
```


```python
import plot_settings
```


```python
import vtuIO
```


```python
import numpy as np
```


```python
import matplotlib.pyplot as plt
import matplotlib.tri as tri
```

## Example problem

In order to demonstrate the features of the problem, we study the example of a tunnel excavation followed by emplacement of a heat-emitting canister. The model simulates the thermal, hydraulic and mechanical response of the system during these two phases. For details on such problems we refer the reader to previous work [@Wang2021].

## 1. Excavation

We first excavate the tunnel by gradually reducing the traction and the pore pressure at the tunnel contour.
This is achieved by a so-called deconfinement curve distributing the excavation over 8 days. The excavated tunnel is then left to drain and consolidate for another 300 days prior to the commencement of heating.


```python
model = OGS(INPUT_FILE="tunnel_ogs6py.prj", PROJECT_FILE="tunnel_exc.prj", MKL=True)
```


```python
model.replace_text("tunnel_exc", xpath="./time_loop/output/prefix")
```


```python
model.write_input()
```




    True



The input file tunnel_ogspy.prj can be build from scratch using ogs6py commands. The corresponding code can be found in create_tunnel.py.
The path to the ogs executable and a name for the logfile containing important information on the simulation run need to be given as well.


```python
model.run_model(path="~/github/ogs/build_mkl/bin", logfile="excavation.log")
```

    OGS finished with project file tunnel_exc.prj.
    Execution took 101.43525815010071 s


The ouput can be eaysily analyzed using the the capabilities of the VTUinterface tool.
It is important to tell vtuIO the dimensionality of the problem in order to use the correct algorithm for interpolation.

One of the most significant features of VTUinterface is the ability to deal with PVD files as time series data.


```python
pvdfile = vtuIO.PVDIO("tunnel_exc.pvd", dim=2)
```

    tunnel_exc.pvd


The folllowing command reads time series data from the PVD and the referenced VTU files.
The default observation point is {'pt0': (0,0,0)} using the method nearest the data at the tunne boundary can be gathered:


```python
excavation_curve = pvdfile.read_time_series("pressure", interpolation_method="nearest")
```


```python
plt.plot(pvdfile.timesteps, excavation_curve["pt0"] / 1e6)
plt.xlabel("$t$ / d")
plt.ylabel("$p$ / MPa");
```


    
![png](output_18_0.png)
    


## 2. Spatially varying properties

Another useful feature in a modelling workflow we wish to demonstrate is the assignment of spatially varying properties, initial conditions, etc. Here, we include a permeability enhancement in the vicinity of the tunnel after excavation in order to mimic the existence of an excavation damaged zone (EDZ) as an illustrative example. Counter to our usual simulations, the EDZ is here only activated in the heating phase in order to keep this demonstration case simple.

To define a field for an existing VTU file, we can define an arbitrary founction depending on three coordinates x,y and z:


```python
R = 2.5
```


```python
def permEDZ(x,y,z):
    r = np.sqrt(x**2+y**2)
    return np.exp(-(r-R)*3)/1e17+1e-20
```


```python
r = np.linspace(R,10,100)
```


```python
plt.plot(r,permEDZ(r,0,0))
plt.axvline(R,ls='--',color='black')
plt.xlabel("$r$ / m")
plt.yscale("log")
plt.ylabel("$k$ / m$^2$");
```


    
![png](output_23_0.png)
    


We read in the last time-step after the excavation:


```python
lasttimestep = vtuIO.VTUIO("tunnel_exc_ts_81_t_8.000000.vtu", dim=2)
```

The the function ist then converted to a point field which is transformed to cell data by the function argument cell=True and written to the file "tunnel_restart.vtu":


```python
lasttimestep.func_to_field(permEDZ, "perm", "tunnel_restart.vtu", cell=True)
```

## 3. Create Input for heating

Now that the properties are set and the initial conditions calculated, we can start the heating simulation. The following input specifies the boundary conditions of the problem and the material properties in the input file for the new phase, which is also based on the original input file used above for the excavation run.

The following set of methods are general purpose methods specially suited for manipulating the OGS6 (XML-) input.


```python
model = OGS(INPUT_FILE="tunnel.prj", PROJECT_FILE="tunnel_heat.prj", MKL=True)
```


```python
model.replace_text("tunnel_restart.vtu", xpath="./meshes/mesh", occurrence=0)
model.replace_text("tunnel_heat", xpath="./time_loop/output/prefix")
model.remove_element("./processes/process/initial_stress")
model.remove_element("./media/medium/properties/property[name='permeability']")
model.remove_element("./parameters/parameter[mesh='tunnel']")
model.add_block("property", parent_xpath="./media/medium/properties", taglist=["name","type", "parameter_name"], textlist=["permeability", "Parameter", "k"])
model.add_block("parameter", parent_xpath="./parameters", taglist=["name","type", "field_name"], textlist=["k", "MeshElement", "perm"])
model.add_block("parameter", parent_xpath="./parameters", taglist=["name","type", "field_name"], textlist=["displacement_exc", "MeshNode", "displacement"])
model.add_block("parameter", parent_xpath="./parameters", taglist=["name","type", "field_name"], textlist=["pressure_exc", "MeshNode", "pressure"])
model.replace_text("displacement_exc", xpath="./process_variables/process_variable[name='displacement']/initial_condition")
model.replace_text("pressure_exc", xpath="./process_variables/process_variable[name='pressure']/initial_condition")
model.remove_element("./process_variables/process_variable[name='displacement']/boundary_conditions/boundary_condition[mesh='tunnel_inner']")
model.remove_element("./process_variables/process_variable[name='pressure']/boundary_conditions/boundary_condition[mesh='tunnel_inner']")
model.add_block("boundary_condition", parent_xpath="./process_variables/process_variable[name='temperature']/boundary_conditions", taglist=["mesh","type", "parameter"], textlist=["tunnel_inner", "Neumann", "heat_bc"])
model.replace_text("100000000", xpath="./time_loop/processes/process/time_stepping/t_end")
model.replace_text("500000", xpath="./time_loop/processes/process/time_stepping/initial_dt")
model.replace_text("50000", xpath="./time_loop/processes/process/time_stepping/minimum_dt")
model.replace_text("500000", xpath="./time_loop/processes/process/time_stepping/maximum_dt")
model.replace_text("10", xpath="./time_loop/output/timesteps/pair/each_steps")
```


```python
model.write_input()
```




    True




```python
model.run_model(path="~/github/ogs/build_mkl/bin", logfile="heating.log")
```

    OGS finished with project file tunnel_heat.prj.
    Execution took 339.61534357070923 s


We now look at the output again and define a set of observation points. We're interested in temperatures as well as pore pressure rise due to thermal pressurization of the fluid.


```python
pvdfile = vtuIO.PVDIO("tunnel_heat.pvd", dim=2)
```

    tunnel_heat.pvd



```python
pts = {"pt0": (3.5,3.5,0), "pt1": (5.5,5.5,0), "pt2": (8.5,8.5,0)}
```


```python
heating_curve = pvdfile.read_time_series("temperature", pts=pts)
pressure_curve = pvdfile.read_time_series("pressure", pts=pts)
```


```python
for pt in pts:
    plt.plot(pvdfile.timesteps/86400, heating_curve[pt]-273.15)
plt.xlabel("$t$ / d")
plt.ylabel("$T$ / °C");
```


    
![png](output_37_0.png)
    



```python
for pt in pts:
    plt.plot(pvdfile.timesteps/86400, pressure_curve[pt] / 1e6)
plt.xlabel("$t$ / d")
plt.ylabel("$p$ / MPa");
#plt.xscale('log')
```


    
![png](output_38_0.png)
    



```python
last_ts_vtu = vtuIO.VTUIO(pvdfile.vtufilenames[-1], dim=2)
```

Without interpolation any field corresponding to the order of node points (saved in .points variable) can be read with the following command.


```python
pressurefield = last_ts_vtu.get_point_field("pressure_interpolated")
```

The available field names can be obtained as well using as single function call:


```python
last_ts_vtu.get_field_names()
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-36-f2ac528b96b7> in <module>
    ----> 1 last_ts_vtu.get_field_names()
    

    AttributeError: 'VTUIO' object has no attribute 'get_field_names'


To make a contour plot matplotlibs triangulation tools can be used:


```python
levels = np.arange(1, 10, 0.5)
```


```python
triang = tri.Triangulation(last_ts_vtu.points[:,0],last_ts_vtu.points[:,1])
```


```python
triang.set_mask(np.hypot(last_ts_vtu.points[:,0][triang.triangles].mean(axis=1),
                         last_ts_vtu.points[:,1][triang.triangles].mean(axis=1))
                < R)
```


```python
plt.tricontourf(triang,pressurefield/1e6, cmap=plt.cm.get_cmap("cool"), levels=levels)
plt.xlabel("$x$ / m")
plt.ylabel("$y$ / m")
plt.colorbar(label='$p$ / MPa')
plt.tight_layout()
```


    
![png](output_48_0.png)
    


Often it is important read out data at arbitraty points within the mesh or along predefined lines.
To do that we need to interpolate beween grid points.
VTUinterface uses scipy.interpolate for interpolation beween grid points, i.e. the user can select between different methods that are provided by scipy.interpolate.

A diagonal point set can be defined as follows:


```python
x = np.linspace(R,50,num=100)
```


```python
diagonal = [(i,i,0) for i in x]
```


```python
interp_methods = ["nearest", "linear", "cubic"]
```

Using three different interpolation methods, we can read a point set array along the diagonal.


```python
p_diagonal = {}
for method in interp_methods:
    p_diagonal[method] = last_ts_vtu.get_point_set_data("pressure_interpolated", pointsetarray=diagonal, interpolation_method=method)
```


```python
r = np.sqrt(2*x*x)
```


```python
for method in interp_methods:
    plt.plot(r[:],p_diagonal[method]/1e6, label=method)
plt.legend()
plt.xlabel("$r$ / m")
plt.ylabel("$p$ / MPa")
plt.tight_layout();
```


    
![png](output_56_0.png)
    


The combination of ogs6py with VTUinterface allows to perform ensemble runs quite easily and to analyze the results directly on-the-fly.
E.g., considering a  distribution of a triangular distributed parameter like the solid thermal expansion coefficient $a_\text{s}$:


```python
a_s_dist = {"low": 1e-6, "mid": 1.e-5, "high": 1.5e-5} 
```

In contrast to the the general purpose methods like replaceTxt and addBlock, there exist also methods for very conveniently replacing Medium, Phase, Parameter properties.
In this example we use replacePhaseProperty() to set the solid thermal expansion coefficient drawn from the given distribution in each iteration.
After execution, the pressure value at given points is read for the last time step and saved in a list.
Parallelization of these kind of ensemble run is straight forwad e.g., using Pythons concurrent future methods.


```python
a_s = []
pressure = []
for i in range(5):
    model = OGS(INPUT_FILE="tunnel_heat.prj", PROJECT_FILE="tunnel_heat_sample.prj", MKL=True)
    a_s.append(np.random.triangular(a_s_dist["low"], a_s_dist["mid"],a_s_dist["high"]))
    model.replace_text("tunnel_heat_sample", xpath="./time_loop/output/prefix")
    model.replace_phase_property(mediumid=0, phase="Solid", name="thermal_expansivity", value=a_s[-1])
    model.write_input()
    model.run_model(path="~/github/ogs/build_mkl/bin", logfile="heating.log")
    pvd = vtuIO.PVDIO("tunnel_heat_sample.pvd")
    last_ts_vtu = vtuIO.VTUIO(pvd.vtufilenames[-1], dim=2)
    p_data = last_ts_vtu.get_point_data("pressure_interpolated", pts=pts)
    pressure.append(p_data["pt2"])
```

    OGS finished with project file tunnel_heat_sample.prj.
    Execution took 363.62722277641296 s
    tunnel_heat_sample.pvd
    OGS finished with project file tunnel_heat_sample.prj.
    Execution took 372.6022951602936 s
    tunnel_heat_sample.pvd
    OGS finished with project file tunnel_heat_sample.prj.
    Execution took 370.30759286880493 s
    tunnel_heat_sample.pvd
    OGS finished with project file tunnel_heat_sample.prj.
    Execution took 330.79134249687195 s
    tunnel_heat_sample.pvd
    OGS finished with project file tunnel_heat_sample.prj.
    Execution took 323.0938148498535 s
    tunnel_heat_sample.pvd



```python
plt.scatter(a_s, np.array(pressure)/1e6)
plt.xlabel('$a_\\mathrm{s}$ / K$^{-1}$')
plt.ylabel('$p$ / MPa')
plt.tight_layout();
```


    
![png](output_61_0.png)
    


ogs6py als has a tool for parsing ogs output.
This can be very helpful for studying numerical stability and performance.
In the following example the output is read and the number or nonlinear iterations needed for every time step are ploted versus the time steps.


```python
out_df = model.parse_out("heating.log")
```


```python
out_df.drop_duplicates(subset ="time_step/number", keep = "last", inplace = True)
```


```python
plt.plot(out_df["time_step/number"], out_df["time_step/iteration/number"])
plt.xlabel("time step")
plt.ylabel("iterations per time step")
plt.tight_layout();
```


    
![png](output_65_0.png)
    


This was a brief overview over the most significant functionalities of ogs6py and VTUinterface.
Future developments will focus on extending functionalities with a focus on built-in checks to ensure that only valid input files are generated.


```python

```

# Acknowledgements

We acknowledge contributions from Tom Fischer, Dmitry Yu. Naumov, Dominik Kern and Sebastian Müller during the genesis of this project.

# References


```python

```
