class MESH(object):
	def __init__(self,**args):
		self.meshfiles=[]
	def addMesh(self,**args):
		if "filename" in args:
			self.meshfiles.append(args["filename"])
	def getMesh(self,**args):
		return self.meshfiles
