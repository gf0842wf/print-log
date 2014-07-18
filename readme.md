## gevent print log ##

### 目的 ###
一般小项目,或者调试时,都习惯用print来写日志,但是发布时,因为print不能存文件,没有时间等信息,所以不是很方便.

通过重定向来解决存文件和添加log的头信息.


### Usage ###

`demo.py`

    # -*- coding: utf-8 -*-
    
    from log import start_logging
    import gevent
    
    start_logging("test.log", timefmt="%Y-%d-%m %X")
    
    print "!", "abcdef", "12345"
    print "+ghighk", "34343"
    print "Dhahaha", "67676"
    print "I", "ooxxx", "88989"
    print "xyzufo", "88989"
            
    gevent.wait()

`test.log`

    [E][2014-18-07 12:32:15] ! abcdef 12345
    [W][2014-18-07 12:32:15] +ghighk 34343
    [D][2014-18-07 12:32:15] Dhahaha 67676
    [I][2014-18-07 12:32:15] I ooxxx 88989
    [-][2014-18-07 12:32:15] xyzufo 88989