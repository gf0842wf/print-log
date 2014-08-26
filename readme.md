## gevent print log ##

### 目的 ###
一般小项目,或者调试时,都习惯用print来写日志,但是发布时,因为print不能存文件,没有时间等信息,所以不是很方便.

支持日志日期信息,支持日志级别.


### Usage ###

支持日志级别: 在print开头添加下面字段即可

    Error, Warn, Debug, Info 
    对应
    !(E),  +(W), =(D),  -(I)

见 `demo.py`