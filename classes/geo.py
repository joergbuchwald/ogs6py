class GEO(object):
	def __init__(self,**args):
		self.geomfile="foobar.gml"
	def addGeom(self,**args):
		if "filename" in args:
			self.geomfile=args['filename']
	def getGeom(self,**args):
		return self.geomfile
