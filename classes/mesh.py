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
    @property
    def tree(self):
        if len(self.meshfiles) == 1:
            if self.axially_symmetric[0] == "false":
                baum = {
                        'mesh': {
                            'tag': 'mesh',
                            'text': self.meshfiles[0],
                            'attr': {},
                            'children': {} } }
            else:
                baum = {
                        'mesh': {
                            'tag': 'mesh',
                            'text': self.meshfiles[0],
                            'attr': { 'axially_symmetric': 'true' },
                            'children': {} } }
        if len(self.meshfiles) > 1:
            baum = { 'meshes': { 'tag': 'meshes', 'text': '', 'attr': {}, 'children': {} } }
            for i, meshfile in enumerate(self.meshfiles):
                if self.axially_symmetric[i] == "false":
                    baum['meshes']['children'][meshfile] = {
                            'tag': 'mesh',
                            'text': meshfile,
                            'attr': {},
                            'children': {} }
                else:
                    baum['meshes']['children'][meshfile] = {
                            'tag': 'mesh',
                            'text': meshfile,
                            'attr': { 'axially_symmetric': 'true' },
                            'children': {} }
        return baum
    def getMesh(self, **args):
        return self.meshfiles
