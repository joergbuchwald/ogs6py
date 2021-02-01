from ogs import *

for i in range(5):
    ofile="new_" + str(i) + ".prj"
    model = OGS(INPUT_FILE="test.prj", PROJECT_FILE=ofile, ogs_mode="silent")
    # general function for replacements
    model.replaceTxt(i/42.1, xpath="./parameters/parameter[name='nu']/value")
    # is the same as:
    #model.replaceTxt(i/42.1, xpath="./parameters/parameter/value", occurance=1)
    # For MPL based processes, the following functions can be used
    # function for replacing parameter properties
    model.replaceParameter(name="E", value=2e9)
    # function for replacing phase properties
    model.replacePhaseProperty(mediumid=0, phase="Solid", name="thermal_expansivity", value="42")
    # function for replacing medium properties
    model.replaceMediumProperty(mediumid=0, name="porosity", value="0.24")
    model.writeInput()
