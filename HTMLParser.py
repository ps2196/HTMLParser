import HTMLParserSimple as sp
from HTMLParserSimple import HTMLElement as HTMLElement
import sys


class HTMLParser (sp.Parser):
    """HTMLParser providing additional filtering and serialization/deserialization functionalities"""

    def __init__(self, file_name, config_html=None):
        sp.Parser.__init__(self, file_name)

        self.filter_elements = None
        self.mapping_elements = None
        self.mappings = {}
        if config_html is not None:
            self.load_config(config_html)

    def load_config(self, config_html):
        """Loads parser config from given HTML"""
        print('LOAD CFG')
        self.mappings = {}
        cf_parser = sp.Parser(config_html)
        if len(cf_parser.elements) == 0:
            return
        if cf_parser.elements[0].tag_name != 'config':
            raise Exception('Config tag missing not found')
        for e in cf_parser.elements[0].sub_elements:
            if e.tag_name == 'extract':
                self.filter_elements = e.sub_elements
            elif e.tag_name == 'map':
                self.mapping_elements = e.sub_elements
                self.load_mapping_config(self.mapping_elements, None)
            else:
                print("Unrecognized element: ", e.tag_name)

    def load_mapping_config(self, mapping_elements, parent_mapping=None):
        """Go through mapping_elements and setup mappings dictionary"""
        for e in mapping_elements:
            nested_mappings = []  # nested tag mappings foun for current element
            if e.tag_name == 'tag':
                tag_mapping = self.mappings.get(e.attributes.get('tag_name'))
                if tag_mapping is not None:
                    raise Exception('Tag ' + e.attributes.get('tag_name') + ' mapping redefined!')
                else:
                    new_mapping = {
                        'module': e.attributes.get('module'),
                        'class': e.attributes.get('class_name'),
                        'constructor': e.attributes.get('method'),
                        'fields': {},
                        'children': []  # nested tag mapping names
                    }
                    self.mappings[e.attributes['tag_name']] = new_mapping
                    for am in e.sub_elements:  # load attribute mapping
                        if am.tag_name == 'attr':
                            new_mapping['fields'][am.attributes['attr_name']] = am.attributes['field']
                        elif am.tag_name == 'tag':
                            nested_mappings.append(am)
            else:
                print('Ommited unrecognized mapping element ' + e.tag_name)
            if len(nested_mappings) > 0:
                self.load_mapping_config(nested_mappings, new_mapping)
            if parent_mapping is not None:
                parent_mapping['children'].append(e.attributes['tag_name'])

    def get_filtered_elements(self):
        """Return a list of elements that fits filter criteria read from self.config_html"""
        filtered_elements = []
        for e in self.elements:
            for fe in self.filter_elements:
                fitting_elements = self._int_get_filtered_elements(e, fe)
                if fitting_elements is not None:
                   filtered_elements.extend(fitting_elements)

        return filtered_elements

    def _int_get_filtered_elements(self, e, fe):
        """Recursively find elements elements that fit filter criteria"""
        res_elements = []
        if self.test_element(e, fe):
            if len(fe.sub_elements) > 0:
                for se in e.sub_elements:
                    for fse in fe.sub_elements:
                        res_elements.extend(self._int_get_filtered_elements(se, fse))
            else:
                res_elements.append(e)
        elif len(e.sub_elements) >= len(fe.sub_elements): #check if current elements nested tags contains any matching elements
            for se in e.sub_elements:
                res_elements.extend(self._int_get_filtered_elements(se, fe))

        return res_elements

    def test_element(self, element, filter_element):
        """Check if element fits the criteria stored in filter_element"""
        if filter_element.tag_name != 'any' and element.tag_name != filter_element.attributes['tag_name']:
            return False
        for fa, fa_val in filter_element.attributes.items():
            if fa == 'tag_name':
                continue  # don't check tag_name attribute
            eatr_val = element.attributes.get(fa)
            if eatr_val is None or eatr_val != fa_val:
                return False

        return True

    def deserialize(self):
        """Returns a collection of python objects created based on parsed HTML and mapping config
         all modules required for creating deserialized object must be pre-imported by users before calling this method"""
        return self.deserialize_elements(self.elements)

    def deserialize_elements(self, elements):
        """Returns a collection of python objects created based on given collection of HTML elements and mapping config
         all modules required for creating deserialized object must be pre-imported by users before calling this method"""
        py_objects = []
        for e in elements:
            py_obj = self.get_py_object_for_element(e)
            if py_obj is not None:
                py_objects.append(py_obj)

        return py_objects

    def get_py_object_for_element(self, e):
        """Returns python object created from given html element"""
        if self.mappings.get(e.tag_name) is None:
            return None
        mc = self.mappings[e.tag_name]  # get mapping config for the element
        mod_name = mc['module']
        mod = sys.modules[mod_name] # get module by its name
        class_o = getattr(mod, mc['class'])
        constr_name = mc['constructor']
        constr = class_o  # use default constructor if not specified in config
        if constr_name is not None:
            constr = getattr(class_o, constr_name)  # use specified method as constructor

        obj = constr()  # create  object using given constructor
        for attr_name, fld_name in mc['fields'].items():
            if e.attributes.get(attr_name) is None:
                continue  # element does not have attribute att_name
            obj.__dict__[fld_name] = e.attributes[attr_name]
        if len(e.sub_elements) > 0 and len(mc['children']) > 0:
            for se in e.sub_elements:
                if se.tag_name in mc['children']:
                    se_obj = self.get_py_object_for_element(se)
                    if se_obj is not None:
                        obj.__dict__[se.tag_name] = se_obj
        return obj

