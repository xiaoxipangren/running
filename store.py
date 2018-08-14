import sqlite3
import os
import time

from log import Logger

logger = Logger(__name__).log()

db_file = 'running.db'

def connect():
    return get_conn(db_file)

def get_conn(path):
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        return conn
    else:
        conn = None
        return sqlite3.connect(':memory:')

def get_cursor(conn):
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()

def execute(sql,data=None,message=None,fetch=False):
    conn = connect()
    cur = get_cursor(conn)
    
    r = None
    if data == None:
        logger.debug('executing sql: [%s]' % sql)
        cur.execute(sql)
        if fetch:
            r = cur.fetchall()
        else:
            conn.commit()
        #logger.debug('execute sql successfully: [%s]' % sql)
    else:
        for d in data:
            logger.debug('executing sql: [{}]-[{}]'.format(sql,d))
            cur.execute(sql,d)
            conn.commit()
            #logger.debug('execute sql successfully: [{}]-[{}]'.format(sql,d))
    if message:
        logger.debug(message)
    close_all(conn,cur)        
            
    return r

def drop_table(table):
    if table is not None and table != '':
        sql = 'DROP TABLE IF EXISTS ' + table
        execute(sql,message='drop table {} successfully'.format(table))

def create_table(sql,table):    
    if sql is not None and sql != '':
        execute(sql,message='create table {} successfully'.format(table))

def close_all(conn, cu):
    try:
        if cu is not None:
            cu.close()
    finally:
        if conn is not None:
            conn.close()

def check(fields,values):
    if values == None or len(values) == 0:
        return False
    if len(fields) != len(values[0]):
        logger.debug('fields not match values')
        return False
    return True

def insert(table,fields,values):
    
    if check(fields,values):
        sql = 'insert into {}({}) values({})'.format(table,','.join(fields),','.join(['?']*len(fields)))
        save(sql,values)

def save(sql, data):
    if sql is not None and sql != '':
        if data is not None:
            execute(sql,data=data)

def update(table,fields,values,condition=None):
    values=[values]
    if check(fields,values):
        sql = 'update {} set {}'.format(table,','.join([field+' = ?' for field in fields]))
        if condition:
            sql = sql + ' where ' + condition
        save(sql,values)

def query(table,fields,condition=None):
    sql = 'select {} from {}'.format(','.join(fields),table)
    if condition:
        sql = sql + ' where ' + condition
    return fetch(sql)

def value(table,field,condition=None):
    models = query(table,[field],condition=condition)
    if models!= None and len(models)>0:
        return models[0][0]
    return None

def fetch(sql):
    if sql != None:
        r = execute(sql,fetch=True)
        return r
    return None

def delete(table,condition):
    sql = 'delete from {} where {}'.format(table,condition)
    execute(sql,message='delete successfully')


def count(table,condition=None):
    return value(table,'count(*)',condition=condition) 

def exists(table,condition):
    num = count(table,condition=condition)
    if num :
        return num > 0
    return False 


def exists_table(table):
    return exists('sqlite_master',"type=='table' and name='%s'" % table)


def init_tables(drop):
    #name－真实姓名　nick－微信昵称　display - 群内昵称
    table_runner =  '''CREATE TABLE `runner` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `name` varchar(100) NOT NULL,
                        `nick` varchar(1000) NOT NULL,
                        `display` varchar(100) NOT NULL,                     
                        `remark` varchar(1000) DEFAULT NULL
                    )'''     
    table_record = '''CREATE TABLE `record` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `rid` integer NOT NULL,                        
                        `date` date DEFAULT NULL,
                        `time` time DEFAULT NULL,                   
                        `distance` decimal(10,5) NOT NULL,
                        `duration` decimal(10,5) DEFAULT NULL,                      
                        `heartrate` int(11)  DEFAULT NULL,
                        `address` varchar(100) DEFAULT NULL,
                        `location` varchar(100) DEFAULT NULL,
                        `remark` varchar(1000) DEFAULT NULL
                    )'''
    table_plan = '''CREATE TABLE `plan` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `rid` integer NOT NULL,                        
                        `month` int(11) NOT NULL,
                        `year` int(11) NOT NULL,                        
                        `plan` decimal(10,5) DEFAULT 60,
                        `duration` decimal(10,5) DEFAULT 0,
                        `total` decimal(10,5) DEFAULT 0,
                        `heartrate` int(11)  DEFAULT NULL,
                        `remark` varchar(1000) DEFAULT NULL
                    )'''             
    table_motto = '''CREATE TABLE `motto` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `rid` integer NOT NULL,                        
                        `date` datetime DEFAULT NULL,
                        `content` varchar(100) DEFAULT NULL,
                        `remark` varchar(1000) DEFAULT NULL
                    )'''
    table_event = '''CREATE TABLE `event` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `start` datetime DEFAULT NULL,
                        `end` datetime DEFAULT NULL,
                        `address` varchar(100) DEFAULT NULL,
                        `location` varchar(100) DEFAULT NULL,
                        `name` varchar(100) NOT NULL,
                        `slogan` varchar(100) DEFAULT NULL,
                        `detail` varchar(100) DEFAULT NULL,
                        `remark` varchar(1000) DEFAULT NULL
                    )'''
    
    table_event_runner='''CREATE TABLE `event_runner` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `eid` integer NOT NULL,
                        `rid` integer NOT NULL,
                        `date` datetime DEFAULT NULL,
                        `remark` varchar(1000) DEFAULT NULL                        
                    )'''

    tables = {
        'runner':table_runner,
        'record':table_record,
        'plan':table_plan,
        'motto':table_motto,
        'event':table_event,
        'event_runner':table_event_runner
    }
    
    for table in tables:
        if drop:
            drop_table(table)
        if not exists_table(table):
            create_table(tables[table],table)


def init(drop=False):
    init_tables(drop)


def test():
    init()

    os.remove(db_file)



if __name__ == '__main__':
    r = exists('runner',"name='张浩'")