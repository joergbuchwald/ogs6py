from ogs import *

for i in range(5):
    ofile="new_" + str(i) + ".prj"
    model = OGS(INPUT_FILE="test.prj", PROJECT_FILE=ofile, ogs_mode="silent")
    model.replaceTxt(i*42.1, xpath="./parameters/parameter/value", occurance=0)
    model.replaceTxt(i/42.1, xpath="./parameters/parameter/value", occurance=1)
    model.writeInput()
