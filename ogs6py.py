# -*- coding: utf-8 -*-
import os
import sys
from lxml import etree as ET
import numpy as np

PROJECT_FILE="project2.prj"
if sys.platform == "win32":
    OGS_NAME="ogs.exe"
else:
    OGS_NAME="ogs"
class OGS(object):
	prjfile=""
#general geom/mesh def
	geomfile="foobar.gml"
	meshfiles=[]
#general process def
	process=np.array([['name', 'type', 'integration_order'],['GW','GROUNDWATER_FLOW','2']])
	primary_variables=np.array([['var', 'name']])
	secondary_variables=np.array([['type', 'internal_name', 'output_name']])
#process specific def
	constitutive_relation={ }
	SM_param=np.array( [['reference_temp','solid_density','specific_body_force'],['300','1','0 0 0']])
	GW_param=np.array([['hydraulic_conductivity'],['1']])
#time loop
	nonlinear_solver="basic_newton"
	time_discretization="BackwardEuler"
	time_stepping="SingleStep"
	t_initial="0"
	t_end="1"
	t_repeat="5"
	t_deltat="0.1"
#timeloop convergence criteria
	convergence_type="DeltaX"
	norm_type="NORM2"
	abstol=""
	reltol=""
#timeloop output
	outputtype=""
	outputprefix=""
	outputvariables=[]
#parameters
	parameters=np.array([['name','type','value','mesh','field_name','expression']])
#initial_conditions
	initial_conditions=np.array([['variable_name','components','order','initial_condition']])
#boundary conditions
	boundary_conditions=np.array([['variable_name','geometrical_set','geometry','mesh','type','component', 'parameter','bc_object']])
#source terms
	source_terms=np.array([['variable_name','geometrical_set','geometry','mesh','type','component', 'parameter','source_term_object']])
#nonlinear solvers
	nonlin_solvers=np.array([['name','type','max_iter','linear_solver','damping']])
#linear solvers
	lin_solver_name=""
	lin_solvers=np.array([['kind','type','preconditioner','max_iter','tol']])
	def __init__(self,**args):
		if "PROJECT_FILE" in args:
			self.prjfile=args['PROJECT_FILE']
		else:
			 self.prjfile=PROJECT_FILE
		self.geomfile="foobar.gml"

#inner class definition
#	class Processvar(object):
#		def __init__(self,**args):
	def addProcessVariable(self,**args):
		if "process_variable" in args:
			if "process_variable_name" in args:
				self.primary_variables=np.append(self.primary_variables,[[args["process_variable"],args["process_variable_name"]]],axis=0)
		if "secondary_variable" in args:
			if "type" in args:
				if "output_name" in args:
					self.secondary_variables=np.append(self.secondary_variables,[[args["type"],args["secondary_variable"],args["output_name"]]],axis=0)
				else:
					print("throw exception")
			else:
				print("throw exception")
	def setIC(self,**args):
		if "process_variable_name" in args:
			if "components" in args:
				if "order" in args:
					if "initial_condition" in args:
						self.initial_conditions=np.append(self.initial_conditions,[[args['process_variable_name'],args['components'],args['order'],args['initial_condition']]],axis=0)
	def addBC(self,**args):
		if "process_variable_name" in args:
			if "type" in args:
				if "geometrical_set" in args:
					if "geometry" in args:
						if "parameter" in args:
							if "component" in args:
								self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],args['geometrical_set'],args['geometry'],'',args['type'],args['component'],args['parameter'],'']],axis=0)
							else:
								self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],args['geometrical_set'],args['geometry'],'',args['type'],'',args['parameter'],'']],axis=0)
						if "bc_object" in args:
							if "component" in args:
								self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],args['geometrical_set'],args['geometry'],'',args['type'],args['component'],'',args['bc_object']]],axis=0)
							else:
								self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],args['geometrical_set'],args['geometry'],'',args['type'],'','',args['bc_object']]],axis=0)
				if "mesh" in args:
					if "parameter" in args:
						if "component" in args:
							self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],'','',args['mesh'],args['type'],args['component'],args['parameter'],'']],axis=0)
						else:
							self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],'','',args['mesh'],args['type'],'',args['parameter'],'']],axis=0)
					if "bc_object" in args:
						if "component" in args:
							self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],'','',args['mesh'],args['type'],args['component'],'',args['bc_object']]],axis=0)
						else:
							self.boundary_conditions=np.append(self.boundary_conditions,[[args['process_variable_name'],'','',args['mesh'],args['type'],'','',args['bc_object']]],axis=0) 	
	def addSourceTerm(self,**args):
		pass
	def getPrimvars(self):
		print(self.primary_variables)
	def getSecvars(self):
		print(self.secondary_variables)
	def addGeom(self,**args):
		if "filename" in args:
			self.geomfile=args["filename"]
	def addMesh(self,**args):
		if "filename" in args:
			self.meshfiles.append(args["filename"])
	def setProcess(self,**args):
		if "name" in args:
			if "type" in args:
				if "integration_order" in args:
					self.process[1,0]=args["name"]
					self.process[1,1]=args["type"]
					self.process[1,2]=args["integration_order"]
					if "reference_temperature" in args:
						self.SM_param[1,0]=args["reference_temperature"]
					if "solid_density" in args:
						self.SM_param[1,1]=args["solid_density"]
					if "specific_body_force" in args:
						self.SM_param[1,2]=args["specific_body_force"]
					if "hydraulic_conductivity" in args:
						self.GW_param[1,0]=args["hydraulic_conductivity"]
	def setProcessRelation(self,**args):
		for i in args:
			self.constitutive_relation[i]=args[i]

	def addTime_loopProcess(self,**args):
		if "nonlinear_solver_name" in args:
			self.nonlinear_solver=args["nonlinear_solver_name"]
			if "convergence_type" in args:
				if args["convergence_type"]=="DeltaX":
					if "norm_type" in args:
						self.convergencetype=args["convergence_type"]
						self.norm_type=args["norm_type"]
						if "abstol" in args:
							self.abstol=args["abstol"]	
						if "reltol" in args:
							self.reltol=args["reltol"]
				if args["convergence_type"]=="PerComponenDeltaX":
					if "norm_type" in args:
						self.convergencetype=args["convergence_type"]
						self.norm_type=args["norm_type"]
						if "abstols" in args:
							self.abstol=args["abstols"]
						if "reltols" in args:
							self.reltol=args["reltols"]
				if args["convergence_type"]=="PercpomponentResidual":
					pass
				if args["convergence_type"]=="Residual":
					pass
			if "time_discretization" in args:
				self.time_discretization=args["time_discretization"]
	def setTime_loopStepping(self,**args):
		if "type" in args:
			if args["type"]=="FixedTimeStepping":
				self.time_stepping="FixedTimeStepping"
				self.t_initial=args["t_initial"]
				self.t_end=args["t_end"]
				if "repeat" in args and "delta_t" in args:
					self.t_repeat=args["repeat"]
					self.t_deltat=args["delta_t"]
			if args["type"]=="SingleStep":
				self.timestepping="SingleStep"
	def addTime_loopOutput(self,**args):
		if "type" in args:
			if "prefix" in args:
				if "variables" in args:
					self.outputtype=args["type"]
					self.outputprefix=args["prefix"]
					self.outputvariables=args["variables"]
	def addNonlinear_solver(self,**args):
		if "name" in args:
			if "type" in args:
				if "max_iter" in args:
					if "linear_solver" in args:
						if "damping" in args:
							self.nonlin_solvers=np.append(self.nonlin_solvers,[[args['name'], args['type'],args['max_iter'],args['linear_solver'],args['damping']]],axis=0)
						else:
							self.nonlin_solvers=np.append(self.nonlin_solvers,[[args['name'], args['type'],args['max_iter'],args['linear_solver'],'']],axis=0)
	def addLinear_solver(self,**args):
		if "name" in args:
			self.lin_solver_name=args['name']
		if "kind" in args:
			if "solver_type" in args:
				if "precon_type" in args:
					if "max_iteration_step" in args:
						if "error_tolerance" in args:
							self.lin_solvers=np.append(self.lin_solvers,[[args['kind'], args['solver_type'], args['precon_type'], args['max_iteration_step'], args['error_tolerance']]],axis=0)
	def addParameter(self,**args):
		if "name" in args:
			if "type" in args:
				if args["type"]=="Constant":
					self.parameters=np.append(self.parameters,[[args['name'], args['type'],args['value'],'','','']],axis=0)
				if args["type"]=="MeshElement" or args["type"]=="MeshNode":
					self.parameters=np.append(self.parameters,[[args['name'], args['type'],'',args['mesh'],args['field_name'],'']],axis=0)
				if args["type"]=="Function":
					self.parameters=np.append(self.parameters,[[args['name'], args['type'],'','','',args['expression']]],axis=0)
	def writeInput(self):
		root=ET.Element("OpenGeoSysProject")
		geometry=ET.SubElement(root,"geometry")
		geometry.text=self.geomfile
		if len(self.meshfiles)>1:
			meshes=ET.SubElement(root,"meshes")
			mesh=[]
			for i in np.arange(0,len(self.meshfiles)):
				mesh.append(ET.SubElement(meshes,"mesh"))
				mesh[i].text=self.meshfiles[i]
		else:
			mesh=ET.SubElement(root,"mesh")
			mesh.text=self.meshfiles[0]
		processes=ET.SubElement(root,"processes")
		process=ET.SubElement(processes, "process")
		process_name=ET.SubElement(process,"name")
		process_name.text=self.process[1,0]
		process_type=ET.SubElement(process,"type")
		process_type.text=self.process[1,1]
		process_integration_order=ET.SubElement(process,"integration_order")
		process_integration_order.text=self.process[1,2]
		if self.process[1,1]=="SMALL_DEFORMATION":
			solid_density=ET.SubElement(process,"solid_density")
			solid_density.text=self.SM_param[1,1]
			reference_temperature=ET.SubElement(process,"reference_temperature")
			reference_temperature.text=self.SM_param[1,0]
			specific_body_force=ET.SubElement(process,"specific_body_force")
			specific_body_force.text=self.SM_param[1,2]
		if self.process[1,1]=="GROUNDWATER_FLOW":
			hydraulic_conductivity=ET.SubElement(process,"hydraulic_conductivity")
			hydraulic_conductivity.text=self.GW_param[1,0]
		if len(self.constitutive_relation)>0:
			const_rel=ET.SubElement(process,"constitutive_relation")
			tag=[]
			k=0
			for i in self.constitutive_relation:
				tag.append(ET.SubElement(const_rel,i))
				tag[k].text=self.constitutive_relation[i]
				k=k+1
		processvars=ET.SubElement(process,"process_variables")
		processvar=[]
		for i in np.arange(1,len(self.primary_variables)):
			processvar.append(ET.SubElement(processvars,self.primary_variables[i,0]))
			processvar[i-1].text=self.primary_variables[i,1]
		secondaryvars=ET.SubElement(process, "secondary_variables")
		secondaryvar=[]
		for i in np.arange(1,len(self.secondary_variables[:,0])):
			secondaryvar.append(ET.SubElement(secondaryvars,"secondary_variable"))
			secondaryvar[i-1].set("type",self.secondary_variables[i,0])
			secondaryvar[i-1].set("internal_name",self.secondary_variables[i,1])
			secondaryvar[i-1].set("output_name",self.secondary_variables[i,2])
		timeloop=ET.SubElement(root,"time_loop")
		tl_processes=ET.SubElement(timeloop,"processes")
		tl_process=ET.SubElement(tl_processes,"process")
		tl_process.set("ref",self.process[1,0])
		tl_process_nonlinsolver=ET.SubElement(tl_process,"nonlinear_solver")
		tl_process_nonlinsolver.text=self.nonlinear_solver
		tl_process_conv_crit=ET.SubElement(tl_process,"convergence_criterion")
		tl_process_conv_crit_type=ET.SubElement(tl_process_conv_crit,"type")
		tl_process_conv_crit_type.text=self.convergence_type
		if self.convergence_type=="DeltaX":
			tl_process_conv_crit_norm=ET.SubElement(tl_process_conv_crit,"norm_type")
			tl_process_conv_crit_norm.text=self.norm_type
			if self.abstol !="":
				tl_process_conv_crit_abstol=ET.SubElement(tl_process_conv_crit,"abstol")
				tl_process_conv_crit_abstol.text=self.abstol
			if self.reltol !="":
				tl_process_conv_crit_reltol=ET.SubElement(tl_process_conv_crit,"reltol")
				tl_process_conv_crit_reltol.text=self.reltol
		if self.convergence_type=="PerComponentDeltaX":
			tl_process_conv_crit_norm=ET.SubElement(tl_process_conv_crit,"norm_type")
			tl_process_conv_crit_norm.text=self.norm_type
			if self.abstol !="":
				tl_process_conv_crit_abstol=ET.SubElement(tl_process_conv_crit,"abstols")
				tl_process_conv_crit_abstol.text=self.abstol
			if self.reltol !="":
				tl_process_conv_crit_reltol=ET.SubElement(tl_process_conv_crit,"reltols")
				tl.process_conv_crit_reltol.text=self.reltol
		tl_process_td=ET.SubElement(tl_process,"time_discretization")
		tl_process_tdtype=ET.SubElement(tl_process_td,"type")
		tl_process_tdtype.text=self.time_discretization
		tl_process_ts=ET.SubElement(tl_process,"time_stepping")
		tl_process_ts_type=ET.SubElement(tl_process_ts,"type")
		tl_process_ts_type.text=self.time_stepping
		tl_process_ts_initial=ET.SubElement(tl_process_ts,"t_initial")
		tl_process_ts_initial.text=self.t_initial
		tl_process_ts_end=ET.SubElement(tl_process_ts,"t_end")
		tl_process_ts_end.text=self.t_end
		tl_process_ts_ts=ET.SubElement(tl_process_ts,"timesteps")
		tl_process_ts_ts_pair=ET.SubElement(tl_process_ts_ts,"pair")
		tl_process_ts_ts_pair_repeat=ET.SubElement(tl_process_ts_ts_pair,"repeat")
		tl_process_ts_ts_pair_repeat.text=self.t_repeat
		tl_process_ts_ts_pair_deltat=ET.SubElement(tl_process_ts_ts_pair,"delta_t")
		tl_process_ts_ts_pair_deltat.text=self.t_deltat
		tl_output=ET.SubElement(timeloop,"output")
		tl_output_type=ET.SubElement(tl_output,"type")
		tl_output_type.text=self.outputtype
		tl_output_prefix=ET.SubElement(tl_output,"prefix")
		tl_output_prefix.text=self.outputprefix
		tl_output_variables=ET.SubElement(tl_output,"variables")
		tl_output_variable=[]
		for i in np.arange(0,len(self.outputvariables)):
			tl_output_variable.append(ET.SubElement(tl_output_variables,"variable"))
			tl_output_variable[i].text=self.outputvariables[i]
		parameters=ET.SubElement(root,"parameters")
		parameter=[]
		para_name=[]
		para_type=[]
		para_mesh=[]
		para_value=[]
		for i in np.arange(0,len(self.parameters)-1):
			parameter.append(ET.SubElement(parameters,"parameter"))
			para_name.append(ET.SubElement(parameter[i],"name"))
			para_name[i].text=self.parameters[i+1,0]
			para_type.append(ET.SubElement(parameter[i],"type"))
			para_type[i].text=self.parameters[i+1,1]
			if self.parameters[i+1,1]=="Constant":
				if len(self.parameters[i+1,2].split())>1:
					para_value.append(ET.SubElement(parameter[i],"values"))
				else:
					para_value.append(ET.SubElement(parameter[i],"value"))
				para_value[i].text=self.parameters[i+1,2]
			if self.parameters[i+1,3]!='':
				para_mesh.append(ET.SubElement(parameter[i],"mesh"))
				para_mesh.text=self.parameters[i+1,3]
			if self.parameters[i+1,1]=="MeshElement" or self.parameters[i+1,1]=="MeshNode":
				para_value.append(ET.SubElement(parameter[i],"field_name"))
				para_value[i].text=self.parameters[i+1,4]
			if self.parameters[i+1,1]=="Function":
				para_value.append(ET.SubElement(parameter[i],"expression"))
				para_value[i].text=self.parameters[i+1,5]	
		procvars=ET.SubElement(root,"process_variables")
		procvar=[]
		procvar_name=[]
		procvar_components=[]
		procvar_order=[]
		procvar_ic=[]
		procvar_bcs=[]
		procvar_bc=[]
		procvar_bc_geomset=[]
		procvar_bc_geometry=[]
		procvar_bc_type=[]
		procvar_bc_mesh=[]
		procvar_bc_component=[]
		procvar_bc_param=[]
		procvar_bc_bcobject=[]
		print("initial conditions:", self.initial_conditions)
		print("boundary conditions:", self.boundary_conditions)
		for i in np.arange(0,len(self.primary_variables[:,0])-1):
			procvar.append(ET.SubElement(procvars,"process_variable"))
			procvar_name.append(ET.SubElement(procvar[i],"name"))
			procvar_name[i].text=self.primary_variables[i+1,1]
			procvar_order.append(ET.SubElement(procvar[i],"order"))
			procvar_components.append(ET.SubElement(procvar[i],"components"))
			procvar_ic.append(ET.SubElement(procvar[i],"initial_condition"))
			for j in np.arange(0,len(self.initial_conditions[:,0])-1):
				if self.initial_conditions[j+1,0]==self.primary_variables[i+1,1]:
					procvar_order[i].text=self.initial_conditions[j+1,2]
					procvar_components[i].text=self.initial_conditions[j+1,1]
					procvar_ic[i].text=self.initial_conditions[j+1,3]
			procvar_bcs.append(ET.SubElement(procvar[i],"boundary_conditions"))
			procvar_bc.append('')
			procvar_bc_geomset.append('')
			procvar_bc_geometry.append('')
			procvar_bc_type.append('')
			procvar_bc_mesh.append('')
			procvar_bc_component.append('')
			procvar_bc_param.append('')
			procvar_bc_bcobject.append('')
			procvar_bc[i]=[]
			procvar_bc_geomset[i]=[]
			procvar_bc_geometry[i]=[]
			procvar_bc_type[i]=[]
			procvar_bc_mesh[i]=[]
			procvar_bc_component[i]=[]
			procvar_bc_param[i]=[]
			procvar_bc_bcobject[i]=[]
			for j in np.arange(0,len(self.boundary_conditions[:,0])-1):
				if self.boundary_conditions[j+1,0]==self.primary_variables[i+1,1]:
					procvar_bc[i].append(ET.SubElement(procvar_bcs[i],"boundary_condition"))
					q=len(procvar_bc[i])-1
					if not self.boundary_conditions[j+1,1]=="":
						procvar_bc_geomset[i].append(ET.SubElement(procvar_bc[i][q],"geometrical_set"))
						procvar_bc_geomset[i][q].text=self.boundary_conditions[j+1,1]
						procvar_bc_geometry[i].append(ET.SubElement(procvar_bc[i][q],"geometry"))
						procvar_bc_geometry[i][q].text=self.boundary_conditions[j+1,2]
						procvar_bc_mesh[i].append('')
					else:
						procvar_bc_geomset[i].append('')
						procvar_bc_geometry[i].append('')
						procvar_bc_mesh[i].append(ET.SubElement(procvar_bc[i][q],"mesh"))
						procvar_bc_mesh[i][q].text=self.boundary_conditions[j+1,3]
					procvar_bc_type[i].append(ET.SubElement(procvar_bc[i][q],"type"))
					procvar_bc_type[i][q].text=self.boundary_conditions[j+1,4]
					if not self.boundary_conditions[j+1,5]=="":
						procvar_bc_component[i].append(ET.SubElement(procvar_bc[i][q],"component"))
						procvar_bc_component[i][q].text=self.boundary_conditions[j+1,5]
					else:
						procvar_bc_component[i].append('')
					if not self.boundary_conditions[j+1,6]=="":
						procvar_bc_param[i].append(ET.SubElement(procvar_bc[i][q],"parameter"))
						procvar_bc_param[i][q].text=self.boundary_conditions[j+1,6]
						procvar_bc_bcobject[i].append('')
					else:
						procvar_bc_param[i].append('')
						procvar_bc_bcobject[i].append(ET.SubElement(procvar_bc[i][q],"bc_object"))
						procvar_bc_bcobject[i][q].text=self.boundary_conditions[j+1,7]
		nonlinsolvers=ET.SubElement(root,"nonlinear_solvers")
		nonlinsolver=[]
		nonlinsolvername=[]
		nonlinsolvertype=[]
		nonlinsolveriter=[]
		nonlinsolverlin=[]
		nonlinsolverdamp=[]
		for i in np.arange(0,len(self.nonlin_solvers[:,0])-1):
			nonlinsolver.append(ET.SubElement(nonlinsolvers,"nonlinear_solver"))
			nonlinsolvername.append(ET.SubElement(nonlinsolver[i],"name"))
			nonlinsolvername[i].text=self.nonlin_solvers[i+1,0]
			nonlinsolvertype.append(ET.SubElement(nonlinsolver[i],"type"))
			nonlinsolvertype[i].text=self.nonlin_solvers[i+1,1]
			nonlinsolveriter.append(ET.SubElement(nonlinsolver[i],"max_iter"))
			nonlinsolveriter[i].text=self.nonlin_solvers[i+1,2]
			nonlinsolverlin.append(ET.SubElement(nonlinsolver[i],"linear_solver"))
			nonlinsolverlin[i].text=self.nonlin_solvers[i+1,3]
			if not self.nonlin_solvers[i+1,4]=="":
				nonlinsolverdamp.append(ET.SubElement(nonlinsolver[i],"damping"))
				nonlinsolverdamp[i].text=self.nonlin_solvers[i+1,4]
			else:
				nonlinsolverdamp.append('')
		linsolvers=ET.SubElement(root,"linear_solvers")
		linsolver=ET.SubElement(linsolvers,"linear_solver")
		linsolvername=ET.SubElement(linsolver,"name")
		linsolvername.text=self.lin_solver_name
		for i in np.arange(0,len(self.lin_solvers[:,0])-1):
			if self.lin_solvers[i+1,0]=="lis":
				lis=ET.SubElement(linsolver,"lis")
				lis.text="-i "+self.lin_solvers[i+1,1]+" -p "+self.lin_solvers[i+1,2] + " -tol "+self.lin_solvers[i+1,4]+" -maxiter "+self.lin_solvers[i+1,3]
			if self.lin_solvers[i+1,0]=="eigen":
				eigen=ET.SubElement(linsolver,"eigen")
				eigentype=ET.SubElement(eigen,"solver_type")
				eigentype.text=self.lin_solvers[i+1,1]
				eigenprecon=ET.SubElement(eigen,"precon_type")
				eigenprecon.text=self.lin_solvers[i+1,2]
				eigenit=ET.SubElement(eigen,"max_iteration_step")
				eigenit.text=self.lin_solvers[i+1,3]
				eigentol=ET.SubElement(eigen,"error_tolerance")
				eigentol.text=self.lin_solvers[i+1,4]
			if self.lin_solvers[i+1,0]=="petsc":
				petsc=ET.SubElement(linsolver,"petsc")
				petscparam=ET.SubElement(petsc,"parameters")
				petscparam.text="-ksp_type "+self.lin_solvers[i+1,1]+" -pc_type "+self.lin_solvers[i+1,2] + " -ksp_rtol "+self.lin_solvers[i+1,4]+" -ksp_max_it "+self.lin_solvers[i+1,3]
				
		tree=ET.ElementTree(root)
		tree.write(self.prjfile, encoding="ISO-8859-1", xml_declaration=True, pretty_print=True)
		return True
	def runModel(self,ogs_root=None,ogs_name=OGS_NAME,print_log=True,save_log=True,log_path=None,	log_name=None,timeout=None,):
		cmd=ogs_name+" "+self.prjfile+" >out"
		os.system(cmd)
		return True
if __name__=='__main__':
#Testmodel:
	model=OGS(PROJECT_FILE="blablubb.prj")
	model.addGeom()
	model.addGeom(filename="geometry.gml")
	model.addMesh(filename="blabubb")
	model.addMesh(filename="qwertz")
	model.setProcess(name="GW",type="GROUNDWATER_FLOW",integration_order="2",hydraulic_conductivity="K")
#	model.setProcessRelation(type="LinearElasticIsotropic",youngs_modulus="E",poissons_ratio="nu")
	model.addProcessVariable(process_variable="process_variable", process_variable_name="displacement")
	model.addProcessVariable(process_variable="process_variable", process_variable_name="displacement2")
	model.addProcessVariable(secondary_variable="stress",type="nice", output_name="sigma")
	model.addProcessVariable(secondary_variable="stress2",type="nice2", output_name="sigma2")
	model.addTime_loopProcess(nonlinear_solver_name="basic_newton",convergence_type="DeltaX", norm_type="NORM2", abstol="1e-12", time_discretization="BackwardEuler")
	model.setTime_loopStepping(type="FixedTimeStepping",t_initial="0",t_end="1",repeat="4",delta_t="0.25")
	model.addTime_loopOutput(type="VTK",prefix="blubb",variables=["bla", "blubb"])
	model.addParameter(name="p_dirichlet1",type="Constant",value="25")
	model.addParameter(name="p_dirichlet2",type="Constant",value="24")
	model.addParameter(name="displacement0",type="Constant",value="0 0 0")
	model.setIC(process_variable_name="displacement", components="3", order="1", initial_condition="displacement0")
	model.addBC(process_variable_name="displacement",geometrical_set="wgdgsrt",geometry="seretarga",type="Dirichlet", component="1", parameter="p_dirichlet1")
	model.addBC(process_variable_name="displacement",geometrical_set="bla",geometry="blubba",type="Dirichlet", component="1", parameter="p_dirichlet2")
	model.addBC(process_variable_name="displacement",mesh="mesh.vtu",type="Dirichlet", component="1", parameter="p_dirichlet2")
	model.setIC(process_variable_name="displacement2", components="3", order="1", initial_condition="displacement1")
	model.addBC(process_variable_name="displacement2",geometrical_set="wwt4w3w5rt",geometry="swrf34ga",type="Dirichlet", component="1", parameter="p_dirichlet1")
	model.addBC(process_variable_name="displacement2",geometrical_set="wwt4w3w5rt",geometry="swrf34ga",type="Dirichlet", component="2", parameter="p_neumann")
	model.addNonlinear_solver(name="basic_picard",type="Picard",max_iter="10",linear_solver="general_linear_solver")
	model.addLinear_solver(name="general_linear_solver", kind="lis",solver_type="cg",precon_type="jacobi",max_iteration_step="10000",error_tolerance="1e-16")
	model.addLinear_solver(name="general_linear_solver", kind="eigen",solver_type="CG",precon_type="Diagonal",max_iteration_step="10000",error_tolerance="1e-16")
	model.addLinear_solver(name="general_linear_solver", kind="petsc",solver_type="cg",precon_type="bjacobi",max_iteration_step="10000",error_tolerance="1e-16")
#inner class usage
#	model.mesh1=OGS().mesh()
#	model.mesh1.addMesh()
	model.writeInput()
	model.runModel()

