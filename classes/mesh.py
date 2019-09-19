class MESH(object):
    def __init__(self, **args):
        self.meshfiles = []
        self.axially_symmetric = []

    def addMesh(self, **args):
        if "filename" in args:
            self.meshfiles.append(args["filename"])
            if "axially_symmetric" in args:
                self.axially_symmetric.append(args["axially_symmetric"])


#                print(self.axially_symmetric)
            else:
                self.axially_symmetric.append("false")
        else:
            raise KeyError("No filename given")

    def getMesh(self, **args):
        return self.meshfiles
