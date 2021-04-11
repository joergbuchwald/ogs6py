from classes import build_tree

class PYTHON_SCRIPT(build_tree.BUILD_TREE):
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
        self._convertargs(args)
        if "filename" in args:
            self.tree['pythonscript']['text'] = args['filename']
        else:
            raise KeyError("No filename given")
