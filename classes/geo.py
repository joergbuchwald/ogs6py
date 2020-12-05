class GEO(object):
    def __init__(self, **args):
        self.tree = {
            'geometry': {
                'tag': 'geometry',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def _convertargs(self, args):
        for item in args:
            args[item] = str(args[item])

    def addGeom(self, **args):
        self._convertargs(args)
        if "filename" in args:
            self.tree['geometry']['text'] = args['filename']
        else:
            raise KeyError("No filename given")
