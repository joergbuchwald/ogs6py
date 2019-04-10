from ogs import *
model=OGS(PROJECT_FILE="thm_test/test.prj")
model.geo.addGeom(filename="square_1x1.gml")
model.mesh.addMesh(filename="quarter_002_2nd.vtu",axially_symmetric="true")
model.processes.setProcess(name="THM",type="THERMO_HYDRO_MECHANICS",
integration_order="4",
dimension="2",
intrinsic_permeability="k",
specific_storage="S", 
biot_coefficient="alpha", 
porosity="phi", 
solid_density="rho_sr", 
fluid_density="rho_fr", 
fluid_viscosity="mu", 
fluid_volumetric_thermal_expansion_coefficient="beta_f", 
solid_linear_thermal_expansion_coefficient="alpha_s", 
solid_specific_heat_capacity="C_s", 
solid_thermal_conductivity="lambda_s", 
fluid_specific_heat_capacity="C_f",
fluid_thermal_conductivity="lambda_f", 
reference_temperature="T0",
specific_body_force="0 0")
model.processes.setConstitutiveRelation(type="LinearElasticIsotropic",youngs_modulus="E",poissons_ratio="nu")
model.processes.addProcessVariable(process_variable="displacement", process_variable_name="displacement")
model.processes.addProcessVariable(process_variable="pressure", process_variable_name="pressure")
model.processes.addProcessVariable(process_variable="temperature", process_variable_name="temperature")
model.processes.addProcessVariable(secondary_variable="sigma",type="static", output_name="sigma")
model.processes.addProcessVariable(secondary_variable="epsilon",type="static", output_name="epsilon")
model.timeloop.addProcess(nonlinear_solver_name="basic_newton",convergence_type="PerComponentDeltaX", norm_type="NORM2", abstols="1e-5 1e-5 1e-5 1e-5", time_discretization="BackwardEuler")
model.timeloop.setStepping(type="FixedTimeStepping",t_initial="0",t_end="50000",repeat="10",delta_t="5000")
model.timeloop.addOutput(type="VTK",prefix="blubb", repeat="1", each_steps="10",variables=["displacement", "pressure", "temperature", "sigma", "epsilon"])
model.parameters.addParameter(name="E",type="Constant",value="5000000000")
model.parameters.addParameter(name="nu",type="Constant",value="0.3")
model.parameters.addParameter(name="k",type="Constant",value="2e-20")
model.parameters.addParameter(name="S",type="Constant",value="0")
model.parameters.addParameter(name="alpha",type="Constant",value="1")
model.parameters.addParameter(name="phi",type="Constant",value="0.16")
model.parameters.addParameter(name="rho_sr",type="Constant",value="2290")
model.parameters.addParameter(name="alpha_s",type="Constant",value="1.5e-5")
model.parameters.addParameter(name="beta_f",type="Constant",value="4e-4")
model.parameters.addParameter(name="lambda_s",type="Constant",value="1.838")
model.parameters.addParameter(name="C_s",type="Constant",value="917.654")
model.parameters.addParameter(name="T0",type="Constant",value="273.15")
model.parameters.addParameter(name="displacement0",type="Constant",value="0 0")
model.parameters.addParameter(name="pressure_ic",type="Constant",value="0")
model.parameters.addParameter(name="dirichlet0",type="Constant",value="0")
model.parameters.addParameter(name="Neumann0",type="Constant",value="0.0")
model.parameters.addParameter(name="temperature_ic",type="Constant",value="273.15")
model.parameters.addParameter(name="pressure_bc_left",type="Constant",value="0")
model.parameters.addParameter(name="temperature_bc_left",type="Constant",value="273.15")
model.parameters.addParameter(name="temperature_source_term",type="Constant",value="150")
model.parameters.addParameter(name="rho_fr",type="Constant",value="999.1")
model.parameters.addParameter(name="mu",type="Constant",value="1e-3")
model.parameters.addParameter(name="C_f",type="Constant",value="4280")
model.parameters.addParameter(name="lambda_f",type="Constant",value="0.6")
model.processvars.setIC(process_variable_name="displacement", components="2", order="2", initial_condition="displacement0")
model.processvars.addBC(process_variable_name="displacement",geometrical_set="square_1x1_geometry",geometry="left",type="Dirichlet", component="0", parameter="dirichlet0")
model.processvars.addBC(process_variable_name="displacement",geometrical_set="square_1x1_geometry",geometry="bottom",type="Dirichlet", component="1", parameter="dirichlet0")
model.processvars.setIC(process_variable_name="pressure", components="1", order="1", initial_condition="pressure_ic")
model.processvars.addBC(process_variable_name="pressure",geometrical_set="square_1x1_geometry",geometry="out",type="Dirichlet", component="0", parameter="pressure_bc_left")
model.processvars.setIC(process_variable_name="temperature", components="1", order="1", initial_condition="temperature_ic")
model.processvars.addBC(process_variable_name="temperature",geometrical_set="square_1x1_geometry",geometry="out",type="Dirichlet", component="0", parameter="temperature_bc_left")
model.processvars.addST(process_variable_name="temperature",geometrical_set="square_1x1_geometry",geometry="center",type="Nodal", parameter="temperature_source_term")
model.nonlinsolvers.addNonlinSolver(name="basic_newton",type="Newton",max_iter="50",linear_solver="general_linear_solver")
model.linsolvers.addLinSolver(name="general_linear_solver", kind="lis",solver_type="bicgstab",precon_type="ilu",max_iteration_step="10000",error_tolerance="1e-16")
model.linsolvers.addLinSolver(name="general_linear_solver", kind="eigen",solver_type="BiCGSTAB",precon_type="ILUT",max_iteration_step="10000",error_tolerance="1e-8")
model.linsolvers.addLinSolver(name="general_linear_solver", kind="petsc",solver_type="cg",precon_type="bjacobi",max_iteration_step="10000",error_tolerance="1e-16")
model.writeInput()
#model.runModel()
