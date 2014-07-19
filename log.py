# -*- coding: utf-8 -*-

from gevent.queue import Queue
from os.path import getsize
import sys, time, os, shutil
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
    # 默认是Debug级别
    levels = {"E":4, "W":3, "D":2, "I":1, "-":2}
    levels2a = {"!":"E", "+":"W", "=":"D", "-":"I",
                "E":"E", "W":"W", "D":"D", "I":"I"}
    
    def __init__(self, filename, queue, timefmt="%Y-%d-%m %X", level="=", bollback=None):
        """
        @param bollback: 日志切割方式 None-不切割;(10, 3)-每个10M(单位为M),保留最近3个文件;("D", 7)-每天一个文件,保留最近10天
        """
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.queue = queue
        self.timefmt = timefmt
        self.sys_level_value = self.levels[self.levels2a.get(level, "D")]
        self.bollback = bollback # 日志分割方式(None, (10, 3), "D")
        self.countfile = 0
        self.gth_loop = gevent.spawn(self.loop)
        self.gth_boll = gevent.spawn(self.incise)
        
    def loop(self):
        while True:
            msg = self.queue.get()
            if msg:
                msg_level = msg[0]
                msg_level = self.levels2a.get(msg_level, "-")
                level_value = self.levels.get(msg_level)
            else: continue
            if level_value < self.sys_level_value: continue
            prefix = "[{0}][{1}] ".format(msg_level, time.strftime(self.timefmt))
            filename = self.filename
            if isinstance(self.bollback,tuple) and self.bollback[0]=="D":
                filename = self.filename + ".%s"%time.strftime("%Y-%m-%d")
            with open(filename, "a+") as f:
                if msg_level != "-" and len(msg) > 1:
                    msg = msg[1:]
                    msg = msg.lstrip(" ")
                line = prefix + msg + "\n"
                f.write(line)
    
    def incise(self):
        if not self.bollback: return
        if not (isinstance(self.bollback, tuple) and len(self.bollback)!=2): return
        value, count = self.bollback
        self.countfile = count
        while True:
            if isinstance(value, int):
                self.incise_size(value, count)
                gevent.sleep(60)
            if isinstance(value, str):
                self.incise_date(value, count)
                gevent.sleep(60*60)
    
    def incise_size(self, megasize, count):
        size = megasize * 1024 * 1024
        filesize = getsize(self.filename)
        if filesize >= size:
            if self.countfile == 0:
                os.remove(self.filename+".%s"%count)
                self.countfile = count
            newfile = self.filename+".%s"%(self.countfile)
            self.countfile -= 1
            shutil.move(self.filename, newfile) # 重命名文件
            with open(self.filename, "w") as f: f.write("") # 新建一个空文件
    
    def incise_date(self, fmt, count):
        listfile = [f for f in os.listdir(self.dirname) if f.startswith(self.basename+".")]
        listfile.sort(reverse=True)
        spare = listfile[count:]
        if spare:
            map(os.remove, spare)
        
                
def start_logging(filename=None, timefmt="%Y-%d-%m %X", level="=", encoding=None, bollback=None):
    """全局函数,启动日志"""
    if not filename: return "sys.stdout"
    queue = Queue()
    stdout = Stdio(queue=queue, encoding=encoding)
    manager = LogManager(filename, queue, timefmt, level, bollback)
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