# -*- coding: utf-8 -*-

class SizedParserBuffer(object):
    """ Buffer sized data """
    def __init__(self, n):
        self.size = n
        self.buffer = ''
        self.received = 0

    @property
    def remaining(self):
        return self.size - self.received

    @property
    def is_finished(self):
        return self.size == self.received

    @property
    def result(self):
        return self.buffer

    def add_data(self, data):
        n = min(self.remaining, data.remaining)
        self.buffer += data.take(n)
        self.received += n
        if (self.remaining == 0):
            return True
        else:
            return False

    def reset(self):
        self.buffer = ''
        self.received = 0

    def __eq__(self, other):
        return self.buffer == other.buffer and self.received == other.received


class UnsizedParserBuffer(object):
    """ unsized parser buffer """
    def __init__(self, terminal, include=False, skip=0):
        self.terminal = terminal
        self.include = include
        self.skip = skip
        self.data = ''
        self.skiped = 0
        self.check_index = 0

    def _add_byte(self, byte):
        if (self.skiped < self.skip):
            self.skiped += 1
            return False
        
        elif (byte == self.terminal[self.check_index]):
            if (self.include):
                self.data += byte
            if (self.check_index == len(self.terminal)-1):
                return True
            else:
                self.check_index += 1
                return False
        else:
            if (self.check_index != 0):
                if (not self.include):
                    self.data += self.terminal[0:self.check_index]
                self.check_index = 0
            self.data += byte
            return False

    def add_data(self, data):
        last = False
        while (data.has_next and not last):
            last = self._add_byte(data.next)
        return last

    @property
    def result(self):
        return self.data

    def reset(self):
        self.data = ''
        self.skiped = 0
        self.check_index = 0

    def __eq__(self, other):
        return self.terminal == other.terminal \
            and self.include == other.include \
            and self.skip == other.skip \
            and self.data == other.data \
            and self.skiped == other.skiped \
            and self.check_index == other.check_index


class Parser(object):
    def parser(self, data):
        raise NotImplementedError()

    def combine(self, other):
        return _Combinater(self, other)

    def precombine(self, other):
        return _PreCombinater(self, other)

    def sufcombine(self, other):
        return _SufCombinater(self, other)

    def then(self, func):
        return _Then(self, func)

    def link(self, func):
        return _Link(self, func)
        


class Byte(Parser):
    """ parser one byte """
    def parser(self, data):
        if (data.has_next):
            return data.next
        else:
            return None

class Bytes(Parser):
    """ parser multi bytes """
    def __init__(self, n):
        self.buffer = SizedParserBuffer(n)
        
    def parser(self, data):
        result = ''
        if (self.buffer.add_data(data)):
            result = self.buffer.result
            self.buffer.reset()
            return result
        else:
            return None


class BytesUntil(Parser):
    """ paresr multi bytes until terminal and The terminus is NOT included in
    the returned value """
    def __init__(self, terminal):
        self.buffer = UnsizedParserBuffer(terminal)

    def parser(self, data):
        result = ''
        if (self.buffer.add_data(data)):
            result = self.buffer.result
            self.buffer.reset()
            return result
        else:
            return None


class _Combinater(Parser):
    """ combine two parser and return result in tuple """
    def __init__(self, parser1, parser2):
        self._parser = (parser1, parser2)
        self._result = ['', '']
        self.index = 0
    def parser(self, data):
        result = self._parser[self.index].parser(data)
        if (result):
            if (self.index == 0):
                self._result[self.index] = result
                self.index += 1
                return self.parser(data)
            else:
                self._result[self.index] = result
                self.index = 0
                return tuple(self._result)
        else:
            None


class _PreCombinater(_Combinater):
    """ combine two parser and return pre parser result """
    def __init__(self, parser1, parser2):
        self._parser = (parser1, parser2)
        self._result = ['', '']
        self.index = 0
    def parser(self, data):
        result = self._parser[self.index].parser(data)
        if (result):
            if (self.index == 0):
                self._result[self.index] = result
                self.index += 1
                return self.parser(data)
            else:
                self._result[self.index] = result
                self.index = 0
                return self._result[0]
        else:
            None


class _SufCombinater(_Combinater):
    """ combine two parser and return suf parser result """
    def __init__(self, parser1, parser2):
        self._parser = (parser1, parser2)
        self._result = ['', '']
        self.index = 0
    def parser(self, data):
        result = self._parser[self.index].parser(data)
        if (result):
            if (self.index == 0):
                self._result[self.index] = result
                self.index += 1
                return self.parser(data)
            else:
                self._result[self.index] = result
                self.index = 0
                return self._result[1]
        else:
            None


class _Then(Parser):

    def __init__(self, parser1, func):
        self.parser1 = parser1
        self.func = func

    def parser(self, data):
        result = self.parser1.parser(data)
        if (result):
            return self.func(result)
        else:
            None

class _Link(Parser):

    def __init__(self, parser1, func):
        self.parser1 = parser1
        self.parser1_complete = False
        self.func = func

    def parser(self, data):
        if (not self.parser1_complete):
            result = self.parser1.parser(data)
            if (result):
                return self.func(result).parser(data)
            else:
                return None
        else:
            return self.func(result)
        
            
        
