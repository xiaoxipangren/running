import time

def year():
    return time.strftime('%Y',time.localtime())

def month():
    return time.strftime('%-m',time.localtime())

def date():
    return time.strftime('%Y-%m-%d',time.localtime())

def now():
    return time.strftime('%X',time.localtime())

def datetime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

def toDatetime(str):
    return time.strptime(str,'%Y-%m-%d %H:%M:%S')

def toTime(str):
    return time.strptime(str,'%X')
def weekday():
    return time.strftime('%w',time.localtime())
def is_weekend():
    day = weekday()
    return day=='0' or day=='6'