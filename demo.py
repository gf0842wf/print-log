# -*- coding: utf-8 -*-

from log import start_logging
import gevent

start_logging("test.log", "%Y-%d-%m %X", level="+")

print "!", "abcdef", "12345"
print "+ghighk", "34343"
print "Dhahaha", "67676"
print "I", "ooxxx", "88989"
print "xyzufo", "88989"
        
gevent.wait()
