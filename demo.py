# -*- coding: utf-8 -*-

from log import start_logging
import gevent

start_logging("./test.log", "%Y-%d-%m %X", level="=", bollback=("D", 15))

print "!", "abcdef", "12345"
print "+ghighk", "34343"
print "-hahaha", "67676"
print "=", "ooxxx", "88989"
print "xyzufo", "88989"
print "!", {"a":2}
        
gevent.wait()
