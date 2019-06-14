from scanner import Scanner

class HTMLElement:

    def __init__(self, name, attributes=None, parent=None):
        """
        :param name: tag name
        :param attributes: dict of element attributes
        :param parent: HTMLElement in which this self is nested
        """
        self.tag_name = name
        self.attributes = {}
        if attributes is not None:
            self.attributes = attributes
        self.parent = parent
        self.sub_elements = []
        self.text = ''# plain text inside a tag

    def __str__(self):
        attr_list = ''
        for a, av in self.attributes.items():
            attr_str = ' '+a+'='
            if '"' in av: # if attr value contains " sourround it with '
                attr_str += "'"+str(av)+"' "
            else: # surround attr value with "
                attr_str += '"' + str(av) + '"'
            attr_list += attr_str
        sub_elements_str = ''
        for se in self.sub_elements:
            sub_elements_str += se.__str__()
        return str('<'+self.tag_name+attr_list+'>'+self.text+sub_elements_str+'</'+self.tag_name+'>')


class Parser:

    def __init__(self, file_name):
        self.scanner = Scanner(file_name)
        self.elements = []
        self.tags_stack = []
        self.doctype = None # Special HTMLElement with DOCTYPE for this html
        self.parse()

    def log(self, msg):
        """Log given message and add info about line and char number"""
        print(msg, ' (line: ', self.scanner.ln(), ", col: ", self.scanner.cn(), ')')

    def tags_stack_top(self):
        """Returns element on top of opened tags stack"""
        if len(self.tags_stack) > 0:
            return self.tags_stack[-1]
        return None

    def parse(self):
        """ Parse given file changing it into list of HTMLElements"""
        self.elements = []
        self.tags_stack = [] # Opened tags are pushed on stack and popped when corresponding closing tag is spotted
        current_symbol = self.scanner.next_symbol()

        while current_symbol.type != Scanner.EOT:
            if current_symbol.type == Scanner.TAG_OPEN:
                self.parse_tag()
            elif current_symbol.type == Scanner.CLOSING_TAG_OPEN:
                self.parse_closing_tag()
            elif current_symbol.type == Scanner.TAG_EXCL_SEQ: # Scanner does not rrutn comments so <! must be doctype declaration
                self.parse_doctype(current_symbol)
            current_symbol = self.scanner.next_symbol()

    def parse_tag(self):
        """Parse a single tag and its attributes - stops after tag close symbol is spotted"""
        symbol = self.scanner.next_symbol()
        if symbol.type != Scanner.HTML_ID:  # ERROR tag name missing
            self.log('Error tag name missing')
            raise Exception('Error tag name missing')
        element = HTMLElement(symbol.text)
        parent_element = self.tags_stack_top()
        element.parent = parent_element
        current_symbol = self.scanner.next_symbol()
        while current_symbol.type not in [Scanner.TAG_CLOSE, Scanner.SINGLE_LINE_TAG_CLOSE, Scanner.EOT]:
            # Obtain attribute name
            attr_name = None
            if current_symbol.type == Scanner.HTML_ID:
                attr_name = current_symbol.text
            else:
                self.log('Attribute list incorrect -  expected attribute name')
                raise Exception('Attribute list incorrect')
            current_symbol = self.scanner.next_symbol()
            # Check name and value should be separatet with assingment symbol
            #print('Symbol type: ',current_symbol.type,"   ", current_symbol.text)
            if current_symbol.type != Scanner.ASSIGN:
                self.log(' Attribute list incomplete - assignment symbol missing')
                raise Exception('Attribute list incorrect')
            # Obtain attribute value
            attr_value = None
            current_symbol = self.scanner.next_symbol()
            if current_symbol.type in [Scanner.SINGLE_QUOTED_TEXT, Scanner.DOUBLE_QUOTED_TEXT]:
                attr_value = current_symbol.text
            else:
                self.log('Attribute list incomplete - attribute value expected')
                raise Exception('Attribute list incorrect')
            element.attributes[attr_name] = attr_value

            current_symbol = self.scanner.next_symbol()

        if current_symbol.type == Scanner.EOT:
            self.log('Tag not closed ', element.tag_name)
        elif current_symbol.type == Scanner.TAG_CLOSE:
            self.tags_stack.append(element)  # tag was properly closed - push it on stack
        # else this was a single line tag

        # Read plain text in chunks and assign it corresponding element
        text = element.text = self.scanner.get_plain_text(256)
        while text != '':
            text = self.scanner.get_plain_text(256)
            element.text += text
        if parent_element is not None:
            parent_element.sub_elements.append(element)
        else: # if current element has no parent assign it to global scope
            self.elements.append(element)

    def parse_closing_tag(self):
        """Parse closing tag and pop corresponding element from stack"""
        current_symbol = self.scanner.next_symbol()
        if current_symbol.type != Scanner.HTML_ID:
            self.log('Closing tag name missing')
            raise Exception('Closing tag name missing')
        tag_name = current_symbol.text
        current_symbol = self.scanner.next_symbol()
        if current_symbol.type != Scanner.TAG_CLOSE:
            self.log('Closing tag expected')
            raise Exception('Closing tag expected')

        top_element = self.tags_stack_top()
        while top_element is not None and top_element.tag_name != tag_name:
            #close all open tag with different names
            self.log('Warning: Closing tag for '+top_element.tag_name+' is missing')
            self.tags_stack.pop()
            top_element = self.tags_stack_top()
        #tag with given name was never opened
        if top_element is None:
            self.log('No corresponding opening tag for ' + tag_name)
            raise Exception('No corresponding opening tag')
        # Close opened tag with given name
        self.tags_stack.pop()

    def parse_doctype(self, current_symbol):
        """Parse '<!' symbol"""
        if (current_symbol.text[2:] != "DOCTYPE"):
            self.log("Html identifier cannot start with !")
            raise Exception('Identifier name incorrect, cannot start with "!"')
        if len(self.elements) > 0:
            self.log('"<!DOCTYPE" should be the very first element')
            raise Exception('"<!DOCTYPE" should be the very first element')
        self.doctype = self.scanner.get_doctype_content()
        if( self.doctype == ''):
            self.log("Warning Empty DOCTYPE element")
        next_symbol = self.scanner.next_symbol()
        if( next_symbol.type != Scanner.TAG_CLOSE):
            self.log("Warrning DOCTYPE is not properly closed")

    def findall(self, tag_name, attributes={}):
        """Returns collection containing all elements that fitts given criteria"""
        res_elems = []
        all_elements = self.elements.copy()
        for e in all_elements:
            if e.tag_name == tag_name:
                e_is_fitting = True
                for attr, attr_val in attributes.items():
                    if self.attributes.get(attr) == attr_val:
                        e_is_fitting = False
                if e_is_fitting:
                    res_elems.append(e)
            all_elements.extend(e.sub_elements)
        return res_elems

    def dump(self):
        """Returns a HTML string matching stored elements structure"""
        html_str =''
        for e in self.elements:
            html_str += e.__str__() + '\n'  # use HTMLElement __str__ method

        return html_str








