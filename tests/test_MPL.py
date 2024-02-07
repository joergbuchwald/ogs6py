from ogs6py.ogs import OGS

# if MKL set vars vars script should be executed before OGS
# model = OGS(PROJECT_FILE="thm_test.prj", MKL=True, OMP_NUM_THREADS=4)
model = OGS(PROJECT_FILE="mpl_test.prj", OMP_NUM_THREADS=4)
model.geo.add_geom(filename="square_1x1_thm.gml")
model.mesh.add_mesh(filename="quarter_002_2nd.vtu", axially_symmetric="true")
model.processes.set_process(
    name="THERMO_HYDRO_MECHANICS",
    type="THERMO_HYDRO_MECHANICS",
    integration_order="4",
)


# model.media.add_property(
#     medium_id="0",
#     name="thermal_conductivity",
#     type="Constant",
#     value="1.2",
# )
model.media.add_property(
    medium_id="0",
    name="thermal_conductivity",
    type="SaturationWeightedThermalConductivity",
    mean_type="geometric",
    dry_thermal_conductivity="0.2",
    wet_thermal_conductivity="1.2",
)

model.media.add_property(
    medium_id="0", name="density", type="WaterDensityIAPWSIF97Region1"
)

model.write_input()
