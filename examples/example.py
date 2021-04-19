from ogs6py import ogs

model = ogs.OGS(PROJECT_FILE="test.prj", MKL=True)
model.geo.addGeom(filename="square_1x1.gml")
model.mesh.addMesh(filename="square_1x1_quad_1e2.vtu")
model.processes.setProcess(name="SD",
                           type="SMALL_DEFORMATION",
                           integration_order="2",
                           solid_density="rho_sr",
                           specific_body_force="0 0")
model.processes.setConstitutiveRelation(type="LinearElasticIsotropic",
                                        youngs_modulus="E",
                                        poissons_ratio="nu")
model.processes.addProcessVariable(process_variable="process_variable",
                                   process_variable_name="displacement")
model.processes.addProcessVariable(secondary_variable="sigma",
                                   output_name="sigma")
model.timeloop.addProcess(process="SD",
                          nonlinear_solver_name="basic_newton",
                          convergence_type="DeltaX",
                          norm_type="NORM2",
                          abstol="1e-15",
                          time_discretization="BackwardEuler")
model.timeloop.setStepping(process="SD", type="FixedTimeStepping",
                           t_initial="0",
                           t_end="1",
                           repeat="4",
                           delta_t="0.25")
model.timeloop.addOutput(type="VTK",
                         prefix="blubb",
                         repeat="1",
                         each_steps="10",
                         variables=["displacement", "sigma"])
model.parameters.addParameter(name="E", type="Constant", value="1")
model.parameters.addParameter(name="nu", type="Constant", value="0.3")
model.parameters.addParameter(name="rho_sr", type="Constant", value="1")
model.parameters.addParameter(name="displacement0",
                              type="Constant",
                              values="0 0")
model.parameters.addParameter(name="dirichlet0", type="Constant", value="0")
model.parameters.addParameter(name="dirichlet1", type="Constant", value="0.05")
model.processvars.setIC(process_variable_name="displacement",
                        components="2",
                        order="1",
                        initial_condition="displacement0")
model.processvars.addBC(process_variable_name="displacement",
                        geometrical_set="square_1x1_geometry",
                        geometry="left",
                        type="Dirichlet",
                        component="0",
                        parameter="dirichlet0")
model.processvars.addBC(process_variable_name="displacement",
                        geometrical_set="square_1x1_geometry",
                        geometry="bottom",
                        type="Dirichlet",
                        component="1",
                        parameter="dirichlet0")
model.processvars.addBC(process_variable_name="displacement",
                        geometrical_set="square_1x1_geometry",
                        geometry="top",
                        type="Dirichlet",
                        component="1",
                        parameter="dirichlet1")
model.nonlinsolvers.addNonlinSolver(name="basic_newton",
                                    type="Newton",
                                    max_iter="4",
                                    linear_solver="general_linear_solver")
model.linsolvers.addLinSolver(name="general_linear_solver",
                              kind="lis",
                              solver_type="cg",
                              precon_type="jacobi",
                              max_iteration_step="10000",
                              error_tolerance="1e-16")
model.linsolvers.addLinSolver(name="general_linear_solver",
                              kind="eigen",
                              solver_type="CG",
                              precon_type="DIAGONAL",
                              max_iteration_step="10000",
                              error_tolerance="1e-16")
model.linsolvers.addLinSolver(name="general_linear_solver",
                              kind="petsc",
                              prefix="sd",
                              solver_type="cg",
                              precon_type="bjacobi",
                              max_iteration_step="10000",
                              error_tolerance="1e-16")
model.writeInput()
model.runModel(LOGFILE="test.log")
#model.runModel(path="/path_to_ogs_bin_dir/")
