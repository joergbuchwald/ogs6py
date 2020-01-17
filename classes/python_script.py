class PYTHON_SCRIPT(object):
    def __init__(self, **args):
        self.tree = {
            'pythonscript': {
                'tag': 'python_script',
                'text': "",
                'attr': {},
                'children': {}
            }
        }

    def setPyscript(self, **args):
        if "filename" in args:
            self.tree['pythonscript']['text'] = args['filename']
        else:
            raise KeyError("No filename given")
