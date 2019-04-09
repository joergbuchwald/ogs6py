class GEO(object):
	def __init__(self,**args):
		self.geomfile=""
	def addGeom(self,**args):
		if "filename" in args:
			self.geomfile=args['filename']
		else:
			raise KeyError("No filename given")		
	def getGeom(self,**args):
		return self.geomfile
