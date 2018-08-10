import time

def year():
    return time.strftime('%Y',time.localtime())

def month():
    return time.strftime('%m',time.localtime())

def date():
    return time.strftime('%Y-%m-%d',time.localtime()) 

def now():
    return time.strftime('%X',time.localtime())