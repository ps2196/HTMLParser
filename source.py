class Source:
    def __init__(self, fname):
        self.ln = 0  # line number
        self.cn = 0  # char number in current line
        self.fname = fname  # file name
        self.stream = open(fname, 'r')
        self._current_char = None  #last char returned by next_char
        self._init_read()#initialise current and next char

    def _init_read(self):
        if self._current_char is None:
            self._current_char = self.stream.read(1)

    def peek(self):
        """ Returns first character from stream without removing it"""
        return self._current_char

    def next_char(self):
        """Returns first character removed from the stream"""
        if self._current_char == '': #EOF
            return ''
        if self._current_char == '\n':
            self.ln += 1
            self.cn = 0
        else:
            self.cn += 1
        ret_val = self._current_char
        self._current_char = self.stream.read(1)

        return ret_val

