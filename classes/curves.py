class CURVES(object):
    def __init__(self, **args):
        self.tree = {
            'curves': {
                'tag': 'curves',
                'text': '',
                'attr': {},
                'children': {}
            }
        }

    def _convertargs(self, args):
        for item in args:
            if not (item == "coords" or item == "values"):
                args[item] = str(args[item])

    def populateTree(self, tag, text='', attr=None, children=None):
        if attr is None:
            attr = {}
        if children is None:
            children = {}
        return {'tag': tag, 'text': text, 'attr': attr, 'children': children}

    def addCurve(self, **args):
        self._convertargs(args)
        if not "name" in args:
            raise KeyError("No curve name given.")
        if not "coords" in args:
            raise KeyError("No coordinates given.")
        if not "values" in args:
            raise KeyError("No values given.")
        print(len(args["coords"]), len(args["values"]))
        if len(args["coords"]) != len(args["values"]):
            raise ValueError("Number of time coordinate points differs from number of values")
        else:
            entries = len(self.tree['curves']['children'])
            self.tree['curves']['children'][
                    'curve' + str(entries)] = self.populateTree('curve',
                                                                children={})
            parameter = self.tree['curves']['children']['curve' +
                                                                str(entries)]
            parameter['children']['name'] = self.populateTree(
                    'name', text=args['name'], children={})
            coord_str = ""
            value_str = ""
            for i, coord in enumerate(args["coords"]):
                if i < (len(args["coords"])-1):
                    coord_str = coord_str + str(coord) + " "
                    value_str = value_str + str(args["values"][i]) + " "
                if i == (len(args["coords"])-1):
                    coord_str = coord_str + str(coord)
                    value_str = value_str + str(args["values"][i])
            parameter['children']['coords'] = self.populateTree(
                    'coords', text=coord_str, children={})
            parameter['children']['values'] = self.populateTree(
                    'values', text=value_str, children={})
