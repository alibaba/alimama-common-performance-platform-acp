#coding:utf-8

class Host:

    def __init__(self, ip, query=None, totalRes=None, availableRes=None, status=None):
        self.ip             = ip
        self.query          = query
        self.totalRes       = totalRes
        self.availableRes   = availableRes
        self.status         = status 
