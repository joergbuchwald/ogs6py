from ogs6py.classes import build_tree

class MESH(build_tree.BUILD_TREE):
    def __init__(self, **args):
        self.meshfiles = []
        self.axially_symmetric = []

    def checkAxSym(self,args):
        axsym = "false"
        if "axially_symmetric" in args:
            if type(args["axially_symmetric"]) is bool:
                if args["axially_symmetric"] is True:
                    axsym = "true"
            else:
                axsym = args["axially_symmetric"]
        return axsym

    def addMesh(self, **args):
        if not "filename" in args:
            raise KeyError("No filename given")
        else:
            self.meshfiles.append((args["filename"], self.checkAxSym(args)))


    @property
    def tree(self):
        baum = {'meshes': {}}
        if len(self.meshfiles) == 1:
            if self.meshfiles[0][1] == "false":
                baum['meshes'] = self.populateTree('mesh', text=self.meshfiles[0][0])
            else:
                baum['meshes'] = self.populateTree('mesh', text=self.meshfiles[0][0],
                        attr={'axially_symmetric': 'true'})
        else:
            baum['meshes'] = self.populateTree('meshes')
            for i, meshfile in enumerate(self.meshfiles):
                if meshfile[1] == "false":
                    baum['meshes']['children'][i] = self.populateTree('mesh', text=meshfile[0], children={})
                else:
                    baum['meshes']['children'][i] = self.populateTree('mesh', text=meshfile[0],
                            attr={'axially_symmetric': 'true'}, children={})
        return baum

