class LOCAL_COORDINATE_SYSTEM(object):
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
        if "basis_vector_0" in args:
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
        else:
            raise KeyError("no vector given")
