from ogs6py.ogs import OGS
"""
This example is based on the file created by example_THM.py.
It is tested with the current master version of OGS (2021-05-20)
"""

for i in range(5):
    ofile="thm_test_parameterset_" + str(i) + ".prj"
    model = OGS(INPUT_FILE="thm_test.prj", PROJECT_FILE=ofile)
    # general function for replacements
    model.replace_text(i*0.1, xpath="./parameters/parameter[name='nu']/value")
    # alternatively we can tell ogs6py to replace the value of the 1st (2nd)
    # occurence of parameters/parameter/value:
    #model.replaceTxt(i/42.1, xpath="./parameters/parameter/value", occurrence=1)
    # For MPL based processes, the following functions can be used
    # function for replacing parameter properties
    model.replace_parameter(name="E", value=2e9)
    # function for replacing phase properties
    model.replace_phase_property(mediumid=0, phase="Solid", name="thermal_expansivity", value="42")
    # function for replacing medium properties
    model.replace_medium_property(mediumid=0, name="porosity", value="0.24")
    model.write_input()
