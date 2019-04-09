import numpy as np
class PROCESSES(object):
	def __init__(self,**args):
		self.process=np.array([['name', 'type', 'integration_order'],['GW','GROUNDWATER_FLOW1234567890','2']])
		self.primary_variables=np.array([['var', 'name']])
		self.secondary_variables=np.array([['type', 'internal_name', 'output_name']])
		self.constitutive_relation={ }
		self.SM_param=np.array( [['reference_temp','solid_density','specific_body_force'],['300','1','0 0 0']])
		self.GW_param=np.array([['hydraulic_conductivity'],['1']])
		self.THM_param={ }
	def addProcessVariable(self,**args):
		if "process_variable" in args:
			if "process_variable_name" in args:
				self.primary_variables=np.append(self.primary_variables,[[args["process_variable"],args["process_variable_name"]]],axis=0)
			else:
				raise KeyError("process_variable_name missing.")
		elif "secondary_variable" in args:
			if "type" in args:
				if "output_name" in args:
					self.secondary_variables=np.append(self.secondary_variables,[[args["type"],args["secondary_variable"],args["output_name"]]],axis=0)
				else:
					raise KeyError("No output_name given.")
			else:
				raise KeyError("type missing")
		else:
			raise KeyError("No process_variable/secondary_variable given.")
	def setProcess(self,**args):
		if "name" in args:
			if "type" in args:
				if "integration_order" in args:
					self.process[1,0]=args["name"]
					self.process[1,1]=args["type"]
					print(args["type"],self.process[1,1])
					self.process[1,2]=args["integration_order"]
					if args["type"]=="GROUNDWATER_FLOW":
						if "hydraulic_conductivity" in args:
							self.GW_param[1,0]=args["hydraulic_conductivity"]
						else:
							raise KeyError("No hydraulic conductivity given")
					if args["type"]=="SMALL_DEFORMATION":
						if "reference_temperature" in args:
							self.SM_param[1,0]=args["reference_temperature"]
						else:
							print("No reference_temperature given")
						if "solid_density" in args:
							self.SM_param[1,1]=args["solid_density"]
						else:
							raise KeyError("No solid density given")
						if "specific_body_force" in args:
							self.SM_param[1,2]=args["specific_body_force"]
						else:
							raise KeyError("No specific_body_force given")
					elif args["type"]=="THERMO_HYDRO_MECHANICS":
						for i in args:
							if not (i=="name" or i=="type" or i=="integration_order"):
								self.THM_param[i]=args[i]
					else:
						raise KeyError("Given process type not (yet) supported.")
				else:
					raise KeyError("integration_order missing.")
			else:
				raise KeyError("type missing.")
		else:
			raise KeyError("No process name given.")					
	def setConstitutiveRelation(self,**args):
		for i in args:
			self.constitutive_relation[i]=args[i]

		

