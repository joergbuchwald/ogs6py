# ogs6py

ogs6py is a python-API for the OpenGeoSys finite element sofware.

Essentially, there are two methods for creating/altering input files.
New files from scratch can be build using method calls for each property.
First, the root class neeeds to be instantiaded:
```
model = OGS(PROJECT_FILE="thm_test/test.prj", ogs_mode="verbose")
```
The standard constructor then loads all sublasses defined in classes folder that are named after the root children elements in the prj file. These classes conatain the respective member functions needed to define a certain property.
E.g.,
```
model.geo.addGeom(filename="square_1x1.gml")
```
After all required properties are definded the input file is writen to PROJECT_FILE via
```
model.writeInput()
```
If ogs can be executed systemwide via the `ogs` command the model can be startet with the command:

```
model.runModel()
```
For further details have a look at the following example:
See example.py/example_THM.py.

Often, it is much more appropriate to modify existing input files. This can be done using the replace method.
Similar to the method described above the OGS class needs to be instanciated with and input and an ouptu file:

```
model = OGS(INPUT_FILE="inputfile.prj", PROJECT_FILE="outputfile.prj")
```
The tag-content can be addressed via an xpath, e.g.,
```
xpath="./parameters/parameter/value"
```
Generally, this xpath is not uniquely defined. As the file is read in from top to bottom we can specify the exact path address by mentioning its occurance starting from 0:
```
model.replaceTxt(42, xpath="./parameters/parameter/value", occurance=0)
```
Alternatively, it is also possibliy to change parameter and medium/phase values via specific functions".
For further examples, see example_replace.py.
