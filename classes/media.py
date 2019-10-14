class MEDIA(object):
    def __init__(self, **args):
        self.tree = { 'media': { 'tag': 'processes', 'text': '', 'attr': {}, 'children': {} } }
        self.tree['media']['children'] = { 'medium': { 'tag': 'process', 'text': '', 'attr': {}, 'children': {} } }
        self.constreltree = { 'tag': 'phase', 'text': '', 'attr': {}, 'children': {} }
        self.proc_vartree = { 'tag': 'property', 'text': '', 'attr': {}, 'children': {} }

    def populateTree(self, tag, text='', attr={}, children={}):
        return { 'tag': tag, 'text': text, 'attr': attr, 'children': children }
    def addMedium(self, **args):
        pass
    def addPhase(self, **args):
        pass
    def addProperty(self, **args):
        pass
