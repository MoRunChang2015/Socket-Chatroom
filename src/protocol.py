from time import time
from datetime import datetime

class Protocol(object):
    def __init__(self):
        super(Protocol, self).__init__()
        self.header = Header()
        self.dataEntity = DataEntity()

class Header(object):
    def __init__(self):
        super(Header, self).__init__()
        self.dict = {}

    def setTime(self, time):
        self.dict['time'] = str(float(time))

    def getTime(self):
        return self.dict['time']

    def setName(self, name):
        self.dict['name'] = name

    def getName(self):
        return self.dict['name']

    def setDatalen(self, dataEntityLen):
        self.dict['datalen'] = dataEntityLen

    def getDatalen(self):
        return self.dict['datalen']

    def setType(self, reqType):
        self.dict['type'] = reqType

    def getType(self):
        return self.dict['type']

    def pack(self):
        package = ''
        for key, value in self.dict.iteritems():
            package += (str(key) + ': ' + str(value) + '\n')
        return package

    def unpack(self, lines):
        for line in lines:
            keyValue = line.split(': ', 1)
            key = keyValue[0]
            value = keyValue[1]
            self.dict[key] = value


class DataEntity(object):
    def __init__(self):
        super(DataEntity, self).__init__()
        self.data = ''

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

    def pack(self):
        return self.data

    def unpack(self, package):
        self.data = package


class Request(Protocol):
    def __init__(self):
        super(Request, self).__init__()

    def generate(self, reqType, time, name, data):
        self.header.setType(reqType)
        self.header.setTime(time)
        self.header.setName(name)
        self.dataEntity.setData(data)
        self.header.setDatalen(len(data))

    def pack(self):
        package = ''
        package += self.header.pack()
        package += self.dataEntity.pack()
        return package

    def unpack(self, package):
        lines = package.split('\n')
        self.header.unpack(lines[0:4])
        self.dataEntity.unpack(''.join(lines[4:]))

    def getType(self):
        return self.header.getType()

    def getTime(self):
        if 'time' in self.header.dict.keys():
            return float(self.header.dict['time'])

    def getName(self):
        if 'name' in self.header.dict.keys():
            return self.header.dict['name']

    def getDatalen(self):
        if 'datalen' in self.header.dict.keys():
            return int(self.header.dict['datalen'])

    def getData(self):
        return self.dataEntity.data


def readTime(timestamp):
    return str(datetime.fromtimestamp(int(timestamp)))


def generateRequest(reqtype, username, data=''):
    req = Request()
    req.generate(reqtype, time(), username, data)
    package = req.pack()
    return package


def handleReuest(package):
    req = Request()
    req.unpack(package)
    return req
