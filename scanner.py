from source import Source


class Token:
    # Special chars escaped with &
    amp_escaped_chars = {
        '&lt': '<',
        '&gt': '>',
        '&amp': '&',
        '&quot': '"',
        '&apos': "'"
    }
    def __init__(self, token_type, chars):
        """ chars - list of characters"""
        self.type = token_type
        self.text = ''.join(chars)
        if Token.amp_escaped_chars.get(self.text) is not None:
            self.text = Token.amp_escaped_chars[self.text]


class Scanner:
    # Token types to ids mapping
    token_types = {
        'EOT': 0,
        'TAG_OPEN': 1,
        'TAG_CLOSE': 2,
        'SINGLE_LINE_TAG_CLOSE': 3,
        '<!_SEQ': 4,
        '&_SEQ': 5,
        'CLOSING_TAG_OPEN': 6,
        'DOUBLE_QUOTED_TEXT': 7,
        'SINGLE_QUOTED_TEXT': 8,
        'PLAIN_TEXT': 9,
        'ASSIGN': 10,
        'COMMENT': 11,
        'PY_ID': 12,
        'HTML_ID': 13
    }
    # Enumerate token types
    EOT = 0
    TAG_OPEN = 1
    TAG_CLOSE = 2
    SINGLE_LINE_TAG_CLOSE = 3
    TAG_EXCL_SEQ = 4
    AMP_SEQ = 5
    CLOSING_TAG_OPEN = 6
    DOUBLE_QUOTED_TEXT = 7
    SINGLE_QUOTED_TEXT = 8
    PLAIN_TEXT = 9
    ASSIGN = 10
    COMMENT = 11
    PY_ID = 12
    HTML_ID = 13

    def __init__(self, fname):
        self.src = Source(fname)  # Data source
        self.chars = []

    def ln(self):
        return self.src.ln

    def cn(self):
        return self.src.cn

    def skip_comment(self):
        """skips comment at the moment of calling this method
        the sequence '<!-- has already been read from source"""
        while True:
            c = self.src.next_char()
            if c == '':
                return # EOF
            # Check if this is comment end sequence '-->'
            if c == '-':
                c = self.src.next_char()
                if c == '-' or c == '':
                    c = self.src.next_char()
                    if c == '>' or c == '':
                        return

    def skip_white_spaces(self):
        c = self.src.peek()
        while c.isspace():  # skip white spaces
            self.src.next_char()
            c = self.src.peek()

    def next_word(self, terminal_char_set = set(), include_terminal_char = False):
        """ Return next word read from src
        Word  ends with a whitespace or a character specified in
        a TERMINAL_CHAR_SET which is empty by default
        Maximum word length is set to 256
        INCLUDE_TERMINAL_CHAR - default false, when true a terminal char is included in result string"""
        self.skip_white_spaces()
        c = self.src.peek()
        i = 0
        while (c != '' and (not c.isspace()) and
                (c not in terminal_char_set) and i < 256):
            i += 1
            c = self.src.next_char()
            self.chars.append(c)
            c = self.src.peek()
        if include_terminal_char and c in terminal_char_set:
            c = self.src.next_char()
            self.chars.append(c)

    def get_doctype_content(self):
        self.chars = []
        c = self.src.peek()
        i = 0
        while (c != '' and c != '>' and i <= 2048 ):
            i += 1
            c = self.src.next_char()
            self.chars.append(c)
            c = self.src.peek()
        return ''.join(self.chars)

    def get_text_enclosed_with(self, enclosing_char):
        """Return text between given enclosing_chars"""
        c = self.src.peek()
        i = 0
        while (c != '' and (c != enclosing_char) and i < 256):
            i += 1
            c = self.src.next_char()
            self.chars.append(c)
            c = self.src.peek()
        if c == enclosing_char:
            c = self.src.next_char()
            self.chars.append(c)

    def get_plain_text(self, size_limit=None):
        """Return plain text read from source
        Default SIZE_LIMIT is not set
        Reading stops when SIZE_LIMIT is reached or '<' char is read"""
        self.chars = []
        c = self.src.peek()
        while(c != '<' and
              (size_limit is not None and len(self.chars) < size_limit)):
            c = self.src.next_char()
            self.chars.append(c)
            c = self.src.peek()
        return ''.join(self.chars)

    def get_html_id(self, max_id_len = 256):
        self.chars = []
        self.skip_white_spaces()
        c = self.src.peek()
        while(c != '' and not c.isspace() and
               (c.isalnum() or c in ['_', '-', '.', ':']) and
               len(self.chars) < max_id_len):
            c = self.src.next_char()
            self.chars.append(c)
            c = self.src.peek()
        return ''.join(self.chars)

    def next_symbol(self):
        """Returns next symbol read from source - this does not retur comment symbols"""
        symbol = self._int_next_symbol()
        while symbol.type == self.COMMENT:
            symbol = self._int_next_symbol()
        return symbol

    def _int_next_symbol(self):
        """Returns next symbol from  source -
        this is a method for internal use inside this class and should not be called outside"""
        self.chars = []# list of characters read from sro

        self.skip_white_spaces()
        c = self.src.next_char()
        self.chars.append(c)

        if c == '':
            return Token(self.token_types["EOT"], [])

        # Tag open
        if c == '<' and self.src.peek() not in ['/', '!']:
            return Token(self.token_types['TAG_OPEN'], self.chars)

        if c == '<' and self.src.peek() == '/':
            c = self.src.next_char()
            self.chars.append(c)
            return Token(self.token_types['CLOSING_TAG_OPEN'], self.chars)

        # '<!' sequence
        if c == '<' and self.src.peek() == '!':
            c = self.src.next_char()
            self.chars.append(c)
            c = self.src.next_char()
            if c == '-'and self.src.peek() == '-': # Comment beginning
                c = self.src.next_char()
                self.skip_comment()
                return Token(self.token_types['COMMENT'], ["<!--"])

            else:
                while c != '' and (not c.isspace()) and c != '=':
                    self.chars.append(c)
                    c = self.src.next_char()
                return Token(self.token_types['<!_SEQ'], self.chars)

        if c == '>':
            return Token(self.token_types['TAG_CLOSE'], self.chars)
        if c == '/' and self.src.peek() == '>':
            c = self.src.next_char()
            self.chars.append(c)
            return Token(self.token_types['SINGLE_LINE_TAG_CLOSE'], self.chars)

        if c == '&':
            self.next_word()
            return Token(self.token_types['&_SEQ'], self.chars)

        if c == '"':
            self.get_text_enclosed_with('"')
            return Token(self.token_types['DOUBLE_QUOTED_TEXT'], self.chars[1:-1])
        if c == "'":
            self.get_text_enclosed_with("'")
            return Token(self.token_types['SINGLE_QUOTED_TEXT'], self.chars[1:-1])
        if c == "=":
            return Token(self.token_types["ASSIGN"], self.chars)

        # this is tag or atrribute name
        self.next_word(set(['<', '>', '/', '&', '=', '"', '"']))
        return Token(self.token_types['HTML_ID'], self.chars)












