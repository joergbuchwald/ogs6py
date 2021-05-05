import sys
from ogs6py.ogs import OGS


def main(filename):
    f = OGS(INPUT_FILE=filename, PROJECT_FILE=filename)
    f.addBlock("property", parent_xpath="./media/medium/properties", taglist=["name","type"], textlist=["thermal_conductivity", "EffectiveThermalConductivityPorosityMixing"])
    f.writeInput()

if __name__ == '__main__':
    main(sys.argv[1])
