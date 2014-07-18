# -*- coding: utf-8 -*-

from gevent.queue import Queue
import sys, time, os
import gevent


class Stdio(object):
    """实现文件接口,用于patch掉sys.stdout"""
    
    mode = "wb"

    def __init__(self, queue, encoding=None):
        self.encoding = encoding or sys.getdefaultencoding()
        self.queue = queue
        self.buf = ""
  
    def close(self):
        pass

    def fileno(self):
        return -1

    def flush(self):
        pass

    def read(self):
        raise IOError("can't read from the log!")

    readline = read
    readlines = read
    seek = read
    tell = read

    def write(self, data):
        if isinstance(data, unicode):
            data = data.encode(self.encoding)
        d = (self.buf + data).split('\n')
        self.buf = d[-1]
        messages = d[0:-1]
        for message in messages:
            self.queue.put(message)

    def writelines(self, lines):
        for line in lines:
            if isinstance(line, unicode):
                line = line.encode(self.encoding)
            self.queue.put(line)


class LogManager(object):
    """gevent的log循环"""
    # 级别: Error, Warn, Debug, Info
    levels = {"!":"E", "+":"W", "=":"D", "-":"I",
             "E":"E", "W":"W", "D":"D", "I":"I",}
    
    def __init__(self, filename, queue, timefmt="%Y-%d-%m %X"):
        self.filename = filename
        self.queue = queue
        self.timefmt = timefmt
        self.gth_loop = gevent.spawn(self.loop)
        
    def loop(self):
        while True:
            msg = self.queue.get()
            if msg: level = self.levels.get(msg[0], "-")
            else: continue
            prefix = "[{0}][{1}] ".format(level, time.strftime(self.timefmt))
            with open(self.filename, "a+") as f:
                line = prefix + msg + "\n"
                f.write(line)
                
def start_logging(filename=None, timefmt="%Y-%d-%m %X", encoding=None):
    """全局函数,启动日志"""
    if not filename: return "sys.stdout"
    queue = Queue()
    stdout = Stdio(queue=queue, encoding=encoding)
    manager = LogManager(filename, queue)
    sys.stdout = stdout
    return filename

if __name__ == "__main__":
    start_logging("test.log")
    
    while True:
        print "!", "abcdef", "12345"
        print "+ghighk", "34343"
        print "Dhahaha", "67676"
        print "I", "ooxxx", "88989"
        print "xyzufo", "88989"
        gevent.sleep(2)
            
gevent.wait()