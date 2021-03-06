# -*- coding: utf-8 -*-

from sora.iobuffer import IOBuffer
from nose.tools import assert_equal

class TestIOBuffer(object):
    
    def setUp(self):
        self.iobuffer = IOBuffer('hello world')

    def test_next(self):
        assert_equal('h', self.iobuffer.next)

    def test_skip(self):
        self.iobuffer.skip(1)
        assert_equal(10, self.iobuffer.remaining)
        self.iobuffer.skip(12)
        assert_equal(0, self.iobuffer.remaining)

    def test_skip_all(self):
        self.iobuffer.skip_all()
        assert_equal(0, self.iobuffer.remaining)

    def test_take(self):
        assert_equal('hello', self.iobuffer.take(5))

    def test_take_all(self):
        assert_equal('hello world', self.iobuffer.take_all)

    def test_take_copy(self):
        assert_equal(IOBuffer('hello world'), self.iobuffer.take_copy)

    def test_remaining(self):
        self.iobuffer.take(5)
        assert_equal(6, self.iobuffer.remaining)

    def test_has_next(self):
        self.iobuffer.take(6)
        assert_equal(True, self.iobuffer.has_next)
        self.iobuffer.take(5)
        assert_equal(False, self.iobuffer.has_next)

    def test_taken(self):
        self.iobuffer.take(5)
        assert_equal(5, self.iobuffer.taken)

    def test_write_to(self):
        class MockTransport(object):
            def write(self, data):
                return len(data)

        self.iobuffer.write_to(MockTransport())
        assert_equal(0, self.iobuffer.remaining)
