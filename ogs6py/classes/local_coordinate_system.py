from ogs6py.classes import build_tree

class LOCAL_COORDINATE_SYSTEM(build_tree.BUILD_TREE):
    def __init__(self, **args):
        self.tree = {
            'local_coordinate_system': {
                'tag': 'local_coordinate_system',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def addBasisVec(self, **args):
        self._convertargs(args)
        if not "basis_vector_0" in args:
            raise KeyError("no vector given")
        else:
            self.tree['local_coordinate_system']['children'] = {
                'basis_vector_0': {
                'tag': 'basis_vector_0',
                'text': args["basis_vector_0"],
                'attr': {},
                'children': {}}}
            if "basis_vector_1" in args:
                self.tree['local_coordinate_system']['children']['basis_vector_1'] = {
                    'tag': 'basis_vector_1',
                    'text': args["basis_vector_1"],
                    'attr': {},
                    'children': {}}
            if "basis_vector_2" in args:
                self.tree['local_coordinate_system']['children']['basis_vector_2'] = {
                'tag': 'basis_vector_2',
                'text': args["basis_vector_2"],
                'attr': {},
                'children': {}}
