# -*- coding: utf-8 -*-

from gevent.queue import Queue
import gevent
import sys, time, os


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
    levels = {"!":4, "+":3, "=":2, "-":1}
    levels2a = {"!":"E", "+":"W", "=":"D", "-":"I"}
    
    buf = [] # TODO: 定时刷新到文件,而不是来一条,打开文件然后写入
    
    def __init__(self, filename, queue, timefmt="%Y-%d-%m %X", level="=", bollback=None):
        """
        @param bollback: 日志切割方式None-不切割;("D", 10)-每天一个文件,保留最近10天
        : 重要: 建议只使用按天分割日志方式
        """
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.basename = os.path.basename(filename)
        self.queue = queue
        self.timefmt = timefmt
        self.sys_level_value = self.levels[level]
        self.bollback = bollback # 日志分割方式 None, (10, 3), ("D", 10)
        self.gth_loop = gevent.spawn(self.loop)
        self.gth_boll = gevent.spawn(self.incise)
        
    def loop(self):
        while True:
            msg = self.queue.get()
            if not msg: continue
            
            msg_level = msg[0]
            if msg_level not in self.levels:
                msg_level = "="
            else:
                msg = msg[1:]
            
            if not msg: continue
            
            level_value = self.levels.get(msg_level)
            if level_value < self.sys_level_value: continue
            
            prefix = "[%s][%s] "%(self.levels2a[msg_level], time.strftime(self.timefmt))
            
            if self.bollback[0]=="D":
                filename = self.filename + ".%s"%time.strftime("%Y-%m-%d")
            else:
                filename = self.filename
                
            line = prefix + msg + "\n"
            with open(filename, "a+") as f:
                f.write(line)
    
    def incise(self):
        if self.bollback == None: return
        kind, count = self.bollback
        while True:
            self.incise_date(kind, count)
            gevent.sleep(60*60*6) # 6小时检查一次
    
    def incise_date(self, kind, count):
        listfile = [f for f in os.listdir(self.dirname) if f.startswith(self.basename+".")]
        listfile.sort(reverse=True)
        spare = listfile[count:]
        if spare: map(lambda f:os.remove(self.dirname+f), spare)
        
                
def start_logging(filename=None, timefmt="%Y-%d-%m %X", level="=", encoding=None, bollback=None):
    """全局函数,启动日志"""
    if not filename: return "sys.stdout"
    queue = Queue()
    stdout = Stdio(queue=queue, encoding=encoding)
    manager = LogManager(filename, queue, timefmt, level, bollback)
    sys.stdout = stdout
    return filename

if __name__ == "__main__":
    start_logging("./test.log")
    
    while True:
        print "!", "abcdef", "12345"
        print "+ghighk", "34343"
        gevent.sleep(2)
            
    gevent.wait()