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

    def addGeom(self, **args):
        if "filename" in args:
            self.tree['geometry']['text'] = args['filename']
        else:
            raise KeyError("No filename given")
