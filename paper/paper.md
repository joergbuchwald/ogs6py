---
title: 'ogs6py and VTUinterface: streamlining OpenGeoSys workflows in python'
tags:
  - Python
  - physics
  - thermo-hydro-mechanics
  - VTU
  - time-series

authors:
  - name: Jörg Buchwald^[corresponding author]
    orcid: 0000-0001-5174-3603
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Thomas Nagel
    orcid: 0000-0001-8459-4616
    affiliation: 2
  - name: Olaf Kolditz
    orcid: 0000-0002-8098-4905
    affiliation: "1, 3"

affiliations:
 - name: Helmholtz Center for Environmental Research - UFZ, Leipzig, Germany
   index: 1
 - name: Technische Universität Bergakademie Freiberg, Germany
   index: 2
 - name: Technische Universität Dresden, Germany
   index: 3
date: 12 May 2021
bibliography: paper.bib

---

# Summary

ogs6py is a python interface for the OpenGeoSys finite element software.
In conjunction with VTUinterface is is possible to streamline modeling workflows
in jupyter notebooks using python.

# Statement of need

Within the last decade python became the quasi-standard for scientific data-analysis
in the modelling commounity. This because of its ease-of-use and flexibility as an open
source dynamic language, the gigantic Python ecosystem, the development of powerfull plotting
libraries and the jupyter notebook.
However, the attractiveness of Phython is not just limited to postprocessing. 
E.g, with the python wrapper for GMSH [@geuzaine2009gmsh] or the tool meshio [@] also pre-processing tasks can
be easily conducted without leaving the IPython command prompt. It is therefore a big advantage 
in usability nowadays for a modeling package if python bindings are provided, not least the ability to facilitate ensemble runs.

As output OpenGeoSys produces VTU files as timeslices collected together by a PVD file.
These can be analyzed typically using Paraview [@ahrens2005paraview]. For interactive Python use there exists the Python 
wrapper for VTK [@schroeder2000visualizing] and some other tools like PyVista [@sullivan2019pyvista] or Mayavi [@ramachandran2011mayavi] proding an easier access to the VTK library.
While there focus is mainly 3D visualization, the _bread and butter_ bussiness of a finite-element-modeler often 
still requires the extraction of time-series data at arbitrarry point in the model domain.
To our knowledge the named packages (with the exception of Paraview) don't have file support for PVDs or time series data yet 
([@pvdissue; @timeseriesissue]

# Ussage


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
```


```python
import matplotlib.pyplot as plt
import matplotlib.tri as tri
```


```python
model = OGS(INPUT_FILE="square_1e2_lin.prj", PROJECT_FILE="square_1e2_lin_out.prj", MKL=True)
```


```python
phi = 0.16
```


```python
model.replaceMediumProperty(mediumid=0, name="porosity", value=phi)
```


```python
model.writeInput()
```




    True




```python
model.runModel(path="~/github/ogs-build/build_mkl_master/bin", LOGFILE="out.log")
```

    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 85.28426861763 s



```python
last_ts_vtu = vtuIO.VTUIO("square_1e0_lin_ts_100_t_500000.000000.vtu", dim=2)
```


```python
pressurefield = last_ts_vtu.getField("pressure_interpolated")
```


```python
triang = tri.Triangulation(last_ts_vtu.points[:,0],last_ts_vtu.points[:,1])
```


```python
plt.tricontourf(triang,pressurefield)
plt.xlabel("x")
plt.ylabel("y")
plt.colorbar()
plt.tight_layout()
```


![png](output_15_0.png)



```python
x = np.linspace(0,10,num=100)
```


```python
diagonal = [(i,i,0) for i in x]
```


```python
interp_methods = ["nearest", "linear", "cubic"]
```


```python
p_diagonal = {}
for method in interp_methods:
    p_diagonal[method] = last_ts_vtu.getPointSetData("pressure_interpolated", pointsetarray=diagonal, interpolation_method=method)
```


```python
r = np.sqrt(2*x*x)
```


```python
for method in interp_methods:
    plt.plot(r[:],p_diagonal[method], label=method)
    plt.xlim((0.0,5))
plt.legend()
plt.xlabel("r / m")
plt.ylabel("p / Pa")
plt.tight_layout()
```


![png](output_21_0.png)



```python
pvdfile = vtuIO.PVDIO(".","square_1e0_lin.pvd", dim=2)
```

    ./square_1e0_lin.pvd



```python
points = {"pt0": (0.1,0.1,0.0), "pt1": (0.2,0.2,0), "pt2": (0.124,0.3,0.0)}
```


```python
p_vs_t = pvdfile.readTimeSeries("pressure_interpolated", points)
```


```python
for pt in points:
    plt.plot(pvdfile.timesteps, p_vs_t[pt], label=pt)
plt.legend()
plt.xlabel("t / s")
plt.ylabel("p / Pa")
plt.tight_layout()
```


![png](output_25_0.png)



```python
phi_dist = {"low": 0.12, "mid": 0.3, "high": 0.36} 
```


```python
phi = []
pressure =[]
for i in range(10):
    model = OGS(INPUT_FILE="square_1e2_lin.prj", PROJECT_FILE="square_1e2_lin_out.prj", MKL=True)
    phi.append(np.random.triangular(phi_dist["low"], phi_dist["mid"],phi_dist["high"]))
    model.replaceMediumProperty(mediumid=0, name="porosity", value=phi[-1])
    model.writeInput()
    model.runModel(path="~/github/ogs-build/build_mkl_master/bin", LOGFILE="out.log")
    last_ts_vtu = vtuIO.VTUIO("square_1e0_lin_ts_100_t_500000.000000.vtu", dim=2)
    p_data = last_ts_vtu.getPointData("pressure_interpolated", pts=points)
    pressure.append(p_data["pt0"])
```

    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 88.08794116973877 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 86.88312768936157 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 84.42618703842163 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 90.0198221206665 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 82.55094814300537 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 87.03411412239075 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 86.81215977668762 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 83.7426118850708 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 86.03023838996887 s
    OGS finished with project file square_1e2_lin_out.prj.
    Execution took 83.28014135360718 s



```python
plt.scatter(phi, pressure)
plt.xlabel('porosity')
plt.ylabel('pressure')
plt.tight_layout()
```


![png](output_28_0.png)



```python
out_df = model.parseOut("out.log")
```


```python
out_df.drop_duplicates(subset ="time_step/number", keep = "last", inplace = True)
```


```python
plt.plot(out_df["time_step/number"], out_df["time_step/iteration/number"])
plt.xlabel("time step")
plt.ylabel("iterations per time step")
plt.tight_layout()
```


![png](output_31_0.png)


# Acknowledgements

We acknowledge contributions from Tom Fischer, Dmitry Yu. Naumov and Dominik Kern
during the genesis of this project.

# References
