#__author__ = 'lenovo'

from exceptions import Exception ,IOError


class ServerNotFound(Exception):
    def __init__(self, errStr = ''):
        Exception.__init__(self)
        self.errStr = errStr


class FileCanNotCreate(IOError):
    def __init__(self,errStr = ''):
        IOError.__init__(self)
        self.errStr = errStr

class D2FILE(Exception):
    def __init__(self,errStr = ''):
        Exception.__init__(self)
        self.errStr = errStr

class NoJsonData(Exception):
    def __init__(self,errStr = ''):
        Exception.__init__(self)
        self.errStr = errStr

class HttpLibError(Exception):
    def __init__(self):
        Exception.__init__(self)

class AppleServerError(Exception):
    def __init__(self):
        Exception.__init__(self)