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
E.g, with the python wrapper for GMSH [@] or the tool meshio [@] also pre-processing tasks can
be easily conducted without leaving the IPython command prompt. It is therefore a big advantage 
in usability nowadays for a modeling package if python bindings are provided, not least the ability to
to facilitate ensemble runs.

As output OpenGeoSys produces VTU files as timeslices collected together by a PVD file.
These can be analyzed typically using Paraview [@]. For interactive Python use there exists the Python 
wrapper for VTK [@] and some other tools like PyVista or Mayavi proding an easier access to the VTK library.
While there focus is mainly 3D visualization, the _bread and butter_ bussiness of a finite-element-modeler often 
still requires the extraction of time-series data at arbitrarry point in the model domain.
To our knowledge the named packages don't support PVDs or time series data yet 
([issue1](https://github.com/pyvista/pyvista/issues/414)[issue2](https://github.com/pyvista/pyvista-support/issues/294)
[researchgate question](https://www.researchgate.net/post/How_to_plot_pvd_file_using_MayaVi)).

# Ussage


```python
from ogs6py.ogs import OGS
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

    OGS execution not successfull. Error code: 1



    ---------------------------------------------------------------------------

    RuntimeError                              Traceback (most recent call last)

    <ipython-input-11-e3981ca132b9> in <module>
    ----> 1 model.runModel(path="~/github/ogs-build/build_mkl_master/bin", LOGFILE="out.log")
    

    /usr/local/lib/python3.9/dist-packages/ogs6py/ogs.py in runModel(self, **args)
         81         else:
         82             print(f"OGS execution not successfull. Error code: {returncode.returncode}")
    ---> 83             raise RuntimeError
         84 
         85     def __dict2xml(self, parent, dictionary):


    RuntimeError: 



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
```


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
```


```python
pvdfile = vtuIO.PVDIO(".","square_1e0_lin.pvd", dim=2)
```


```python
points = {"pt0": (0.1,0.1,0.0), "pt1": (0.2,0.2,0), "pt2": (0.124,0.3,0.0)}
```


```python
p_vs_t = pvdfile.readTimeSeries("pressure_interpolated", points)
```


```python
for pt in points:
    plt.plot(pvdfile.timesteps, p_vs_t[pt])
```


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
    model.runModel(path="/home/buchwalj/github/ogs/build_mkl/bin", LOGFILE="out.log")
    last_ts_vtu = vtuIO.VTUIO("square_1e0_lin_ts_100_t_500000.000000.vtu", dim=2)
    p_data = last_ts_vtu.getPointData("pressure_interpolated", pts=points)
    pressure.append(p_data["pt0"])
```


```python
plt.scatter(phi, pressure)
plt.xlabel('porosity')
plt.ylabel('pressure')
```



# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References



```python

```
