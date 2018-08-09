import sqlite3

import os
import time

#global var
#数据库文件绝句路径
DB_FILE_PATH = ''
#表名称
TABLE_NAME = ''
#是否打印sql
SHOW_SQL = True

db_file = 'running.db'

def connect():
    return get_conn(db_file)

def get_conn(path):
    '''获取到数据库的连接对象，参数为数据库文件的绝对路径
    如果传递的参数是存在，并且是文件，那么就返回硬盘上面改
    路径下的数据库文件的连接对象；否则，返回内存中的数据接
    连接对象'''
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        print('硬盘上面:[{}]'.format(path))
        return conn
    else:
        conn = None
        print('内存上面:[:memory:]')
        return sqlite3.connect(':memory:')

def get_cursor(conn):
    '''该方法是获取数据库的游标对象，参数为数据库的连接对象
    如果数据库的连接对象不为None，则返回数据库连接对象所创
    建的游标对象；否则返回一个游标对象，该对象是内存中数据
    库连接对象所创建的游标对象'''
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()

def drop_table(table):
    '''如果表存在,则删除表，如果表中存在数据的时候，使用该
    方法的时候要慎用！'''

    if table is not None and table != '':
        conn = connect()
        sql = 'DROP TABLE IF EXISTS ' + table
        if SHOW_SQL:
            print('执行sql:[{}]'.format(sql))
        cu = get_cursor(conn)
        cu.execute(sql)
        conn.commit()
        print('删除数据库表[{}]成功!'.format(table))
        close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))

def create_table(sql):
    '''创建数据库表：student'''
    
    if sql is not None and sql != '':
        conn = connect()
        cu = get_cursor(conn)
        if SHOW_SQL:
            print('执行sql:[{}]'.format(sql))
        cu.execute(sql)
        conn.commit()
        print('创建数据库表成功!')
        close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))


def close_all(conn, cu):
    '''关闭数据库游标对象和数据库连接对象'''
    try:
        if cu is not None:
            cu.close()
    finally:
        if conn is not None:
            conn.close()


def save(sql, data):
    '''插入数据'''
    if sql is not None and sql != '':
        if data is not None:
            conn = connect()
            cu = get_cursor(conn)
            for d in data:
                if SHOW_SQL:
                    print('执行sql:[{}],参数:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))

def fetchall(sql):
    '''查询所有数据'''
    
    if sql is not None and sql != '':
        conn = connect()
        cu = get_cursor(conn)
        if SHOW_SQL:
            print('执行sql:[{}]'.format(sql))
        cu.execute(sql)
        r = cu.fetchall()
        if len(r) > 0:
            for e in range(len(r)):
                print(r[e])
    else:
        print('the [{}] is empty or equal None!'.format(sql)) 

def fetchone(sql, data):
    '''查询一条数据'''
    if sql is not None and sql != '':
        if data is not None:
            conn = connect()
            #Do this instead
            d = (data,) 
            cu = get_cursor(conn)
            if SHOW_SQL:
                print('执行sql:[{}],参数:[{}]'.format(sql, data))
            cu.execute(sql, d)
            r = cu.fetchall()
            if len(r) > 0:
                for e in range(len(r)):
                    print(r[e])
        else:
            print('the [{}] equal None!'.format(data))
    else:
        print('the [{}] is empty or equal None!'.format(sql))

def update(sql, data):
    '''更新数据'''
    if sql is not None and sql != '':
        if data is not None:
            conn = connect()
            cu = get_cursor(conn)
            for d in data:
                if SHOW_SQL:
                    print('执行sql:[{}],参数:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))

def delete(sql, data):
    '''删除数据'''
    if sql is not None and sql != '':
        if data is not None:
            conn = connect()
            cu = get_cursor(conn)
            for d in data:
                if SHOW_SQL:
                    print('执行sql:[{}],参数:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn, cu)
    else:
        print('the [{}] is empty or equal None!'.format(sql))

def save_test():
    '''保存数据测试...'''
    print('保存数据测试...')
    save_sql = '''INSERT INTO record(name,date,distance,duration) values (?, ?, ?, ?)'''
    now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    data = [('测试１',now, 20, 20.3),
            ('测试２', now, 22, 20.3),
            ('测试３', now, 18, 20.3),
            ('测试４', now, 21, 20.3)]
    save(save_sql, data)

def fetchall_test():
    '''查询所有数据...'''
    print('查询所有数据...')
    fetchall_sql = '''SELECT * FROM record'''
    fetchall(fetchall_sql)

def init_tables():
    drop_table('record')
    drop_table('motto')      
    table_record = '''CREATE TABLE `record` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `name` varchar(50) NOT NULL,
                        `nick` varchar(50) DEFAULT NULL,
                        `date` datetime DEFAULT NULL,
                        `distance` decimal(10,5) NOT NULL,
                        `duration` decimal(10,5) DEFAULT NULL,                      
                        `heartrate` int(11)  DEFAULT NULL,
                        `address` varchar(100) DEFAULT NULL,
                        `location` varchar(100) DEFAULT NULL,
                        `remark` varchar(100) DEFAULT NULL
                    )'''
    table_plan = '''CREATE TABLE `plan` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `name` varchar(50) NOT NULL,
                        `nick` varchar(50) DEFAULT NULL,
                        `month` int(11) NOT NULL,
                        `pland` decimal(10,5) DEFAULT 60,
                        `duration` decimal(10,5) DEFAULT NULL,
                        `reald` decimal(10,5) DEFAULT NULL,
                        `heartrate` int(11)  DEFAULT NULL,
                        `remark` varchar(100) DEFAULT NULL
                    )'''             
    table_motto = '''CREATE TABLE `motto` (
                        `id` integer PRIMARY KEY AUTOINCREMENT,
                        `name` varchar(50) NOT NULL,
                        `nick` varchar(50) DEFAULT NULL,
                        `date` datetime DEFAULT NULL,
                        `content` varchar(100) DEFAULT NULL,
                        `remark` varchar(100) DEFAULT NULL
                    )'''
    create_table(table_record)
    create_table(table_motto)


def init():
    inited = os.path.exists(db_file)
    if not inited:
        init_tables()

def test():
    global SHOW_SQL
    SHOW_SQL = True

    init()

    save_test()
    fetchall_test()

    os.remove(db_file)

if __name__ == '__main__':
    test()