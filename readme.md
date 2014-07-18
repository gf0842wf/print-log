## gevent print log ##

### 目的 ###
一般小项目,或者调试时,都习惯用print来写日志,但是发布时,因为print不能存文件,没有时间等信息,所以不是很方便.

支持日志日期信息,支持日志级别.


### Usage ###

支持日志级别: 在print开头添加下面字段即可

    Error, Warn, Debug, Info 
    对应
    !(E),  +(W), =(D),  -(I)

`demo.py`

    # -*- coding: utf-8 -*-
    
    from log import start_logging
    import gevent
    
    start_logging("test.log", timefmt="%Y-%d-%m %X", level="+")
    
    print "!", "abcdef", "12345"
    print "+ghighk", "34343"
    print "Dhahaha", "67676"
    print "I", "ooxxx", "88989"
    print "xyzufo", "88989"
            
    gevent.wait()

`test.log`

    [E][2014-18-07 13:18:47] abcdef 12345
    [W][2014-18-07 13:18:47] ghighk 34343