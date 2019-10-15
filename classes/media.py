class MEDIA(object):
    def __init__(self, **args):
        self.tree = { 'media': { 'tag': 'media', 'text': '', 'attr': {}, 'children': {} } }
        self.constreltree = { 'tag': 'phase', 'text': '', 'attr': {}, 'children': {} }
        self.proc_vartree = { 'tag': 'property', 'text': '', 'attr': {}, 'children': {} }

    def populateTree(self, tag, text='', attr={}, children={}):
        return { 'tag': tag, 'text': text, 'attr': attr, 'children': children }
    def addProperty(self, **args):
        if "medium_id" in args:
            try:
                medium = self.tree['media']['children'][args['medium_id']]
            except KeyError:
                self.tree['media']['children'][args['medium_id']] = { 'tag': 'medium', 'text': '', 'attr': { 'id': args['medium_id'] }, 'children': {} }
                medium = self.tree['media']['children'][args['medium_id']]
            if "phase_type" in args:
                if not 'phases' in medium['children']:
                    medium['children']['phases'] = { 'tag': 'phases', 'text': '', 'attr': { }, 'children': {} }
                try:
                    phase_ = medium['children']['phases']['children'][args['phase_type']]
                except:
                    medium['children']['phases']['children'][args['phase_type']] = { 'tag': 'phase', 'text': '', 'attr': { }, 'children': {} }
                    phase_ = medium['children']['phases']['children'][args['phase_type']]
                    phase_['children'][args['phase_type']] = { 'tag': 'type', 'text': args['phase_type'], 'attr': { }, 'children': {} }
                    phase_['children']['properties'] = { 'tag': 'properties', 'text': '', 'attr': {  }, 'children': {} }
            phase = phase_['children']['properties']['children']
            phase[args['name']] = { 'tag': 'property', 'text': '', 'attr': {  }, 'children': {} }
            phase[args['name']]['children'][args['name']]= { 'tag': 'name', 'text': args['name'], 'attr': {  }, 'children': {} }
            phase[args['name']]['children'][args['type']]= { 'tag': 'type', 'text': args['type'], 'attr': {  }, 'children': {} }
            phase[args['name']]['children'][args['value']]= { 'tag': 'value', 'text': args['value'], 'attr': {  }, 'children': {} }


