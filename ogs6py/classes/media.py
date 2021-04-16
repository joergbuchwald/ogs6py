from ogs6py.classes import build_tree

class MEDIA(build_tree.BUILD_TREE):
    def __init__(self, **args):
        self.tree = {
            'media': {
                'tag': 'media',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def addProperty(self, **args):
        self._convertargs(args)
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
            else:
                try:
                    properies = medium['children']['properties']
                except KeyError:
                    medium['children']['properties'] = {
                        'tag': 'properties',
                        'text': '',
                        'attr': {},
                        'children': {}
                    }
                phase_ = medium
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
            elif args['type'] == "Parameter":
                phase[args['name']]['children']['parameter'] = {
                      'tag': 'parameter_name',
                      'text': args['parameter_name'],
                      'attr': {},
                      'children': {}
                  }

