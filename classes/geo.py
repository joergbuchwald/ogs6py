from classes import build_tree

class GEO(build_tree.BUILD_TREE):
    def __init__(self, **args):
        self.tree = {
            'geometry': {
                'tag': 'geometry',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def addGeom(self, **args):
        self._convertargs(args)
        if "filename" in args:
            self.tree['geometry']['text'] = args['filename']
        else:
            raise KeyError("No filename given")
