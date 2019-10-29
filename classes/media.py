class MEDIA(object):
    def __init__(self, **args):
        self.tree = {
            'media': {
                'tag': 'media',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def populateTree(self, tag, text='', attr={}, children={}):
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}

    def addProperty(self, **args):
        if "medium_id" in args:
            try:
                medium = self.tree['media']['children'][args['medium_id']]
            except KeyError:
                self.tree['media']['children'][args['medium_id']] = {
                        'tag': 'medium',
                        'text': '',
                        'attr': {
                        'id': args['medium_id']},
                        'children': {}
                }
                medium = self.tree['media']['children'][args['medium_id']]
            if "phase_type" in args:
                if not 'phases' in medium['children']:
                    medium['children']['phases'] = {
                        'tag': 'phases',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
                try:
                    phase_ = medium['children']['phases']['children'][
                        args['phase_type']]
                except:
                    medium['children']['phases']['children'][
                        args['phase_type']] = {
                            'tag': 'phase',
                            'text': '',
                            'attr': {},
                            'children': {}
                        }
                    phase_ = medium['children']['phases']['children'][
                        args['phase_type']]
                    phase_['children'][args['phase_type']] = {
                        'tag': 'type',
                        'text': args['phase_type'],
                        'attr': {},
                        'children': {}
                    }
                    phase_['children']['properties'] = {
                        'tag': 'properties',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
            phase = phase_['children']['properties']['children']
            phase[args['name']] = {
                'tag': 'property',
                'text': '',
                'attr': {},
                'children': {}
            }
            phase[args['name']]['children']['name'] = {
                'tag': 'name',
                'text': args['name'],
                'attr': {},
                'children': {}
            }
            phase[args['name']]['children']['type'] = {
                'tag': 'type',
                'text': args['type'],
                'attr': {},
                'children': {}
            }
            if args['type'] == "Constant":
                phase[args['name']]['children']['value'] = {
                    'tag': 'value',
                    'text': args['value'],
                    'attr': {},
                    'children': {}
                }
            elif args['type'] == "Linear":
                phase[args['name']]['children']['reference_value'] = {
                    'tag': 'reference_value',
                    'text': args['reference_value'],
                    'attr': {},
                    'children': {}
                }
                phase[args['name']]['children']['independent_variable'] = {
                    'tag': 'independent_variable',
                    'text': '',
                    'attr': {},
                    'children': {}
                }
                indep_var = phase[args['name']]['children']['independent_variable']['children']
                indep_var['variable_name'] = {
                    'tag': 'variable_name',
                    'text': args['variable_name'],
                    'attr': {},
                    'children': {}
                }
                indep_var['reference_condition'] = {
                    'tag': 'reference_condition',
                    'text': args['reference_condition'],
                    'attr': {},
                    'children': {}
                }
                indep_var['slope'] = {
                    'tag': 'slope',
                    'text': args['slope'],
                    'attr': {},
                    'children': {}
                }
