import itchat
import re
import store
import date
import random
import sys

from log import Logger

test_room='test'
runing_club='珞珈跑团'

#'qi':'#qi',
keys={
    'run':'#run',
    'help':'#help',
    'motto':'#motto',
    'rose':'#rose',
    'qi':'#qi'
}

today_motto=''

mottos=[
    '奔跑吧，大胸弟',
    'just do running',
    '当你跑步时，你在想村上春是哪种树',
    '我是奔跑的五花肉，我为自己带盐',
    '跑步是为了更愉快的喝酒',
    '我跑故我在',
    'RUN,GUMP,RUN!',
    '已离家Five hundred miles，我该怎么回去'
]

room = test_room # runing_club

logger = Logger(__name__).log()

error = None

def filter_chatroom(msg):
    from_user = msg['User']['NickName']
    if(from_user!=room):
        return False
    return True

def reply(msg,filter=filter_chatroom):
    logger.debug('receive message: %s' % msg)
    result = filter(msg)
    if not result:
        return None
    else:
        text = msg['Text'].strip()
        display = msg['ActualNickName']
        logger.debug('%s said: %s' % (display,text))
        return dispatch(display,text)

def dispatch(display,text):
    if do_not_disturb():
        return None
    for key in keys:
        prefix = keys[key]
        if text.startswith(prefix):
            reply_fn = getattr(__import__(__name__),'%s_reply' % key,None)
            if not none_or_empty(reply_fn):
                text = text.replace(prefix,'').strip()
                logger.debug('call reply fn %s' % reply_fn)
                response =  reply_fn(display,text)
                if not none_or_empty(error):
                    global error
                    response = error
                    error = ''
                return response
    return None


#免打扰
def do_not_disturb():
    morning_begin = date.toTime('05:00:00')
    morning_end = date.toTime('10:00:00') if date.is_weekend() else date.toTime('08:00:00')

    evening_begin = date.toTime('19:00:00')
    evening_end = date.toTime('22:00:00')

    now = date.toTime(date.now())

    return not ((now>morning_begin and now<morning_end) or (now>evening_begin and now<evening_end))
    



def test_reply(display,text):
    logger.debug('test reply %s' % text)


def run_reply(display,text):
    data = extra_run(text)   
    if data:
        name = data[0]
        cols = data[1]
        run(display,name,cols)
        #考虑增加使用名字作为识别标志进行他人辅助打卡功能
    global error
    if not none_or_empty(error):
        return error
    return realtime_reply()

def motto_reply(display,text):
    if none_or_empty(text):
        return None

    if len(text.split('\n'))>4:
        global error
        error = '箴言最多4行'
        return None

    id,name,nick = runner(display)
    store.insert('motto',['rid','content','date'],[[id,text,date.date()]])
    return '已添加，将随机展示'


def qi_reply(display,text):
    id,name,nick = runner(display)
    if not is_qi_captain(name,nick,display):
        global error
        error='指令#qi为齐队专属指令'
        return None

    motto_reply(display,text)
    global today_motto
    today_motto = text

    return realtime_reply()


def is_qi_captain(name,nick,display):
    return name=='齐队' or nick == 'AVIC 齐连惠' or display == '齐连惠航天科技88遥感'


def rose_reply(display,text):
    if not none_or_empty(text):
        update_name(display,text)
    
    rose = event('七夕西湖玫瑰跑')

    eid = rose[0]
    table = 'event_runner'
    rid,name,nick = runner(display)
    condition = cond({'eid':eid,'rid':rid})
    if store.exists(table,condition=condition):
        store.delete(table,condition)
    else:
        store.insert(table,['eid','rid','date'],[[eid,rid,date.datetime()]])
    
    return event_rank(rose) 
    

def event_rank(event):
    table = 'event_runner inner join runner on event_runner.rid=runner.id'
    eid = event[0]
    runners = store.query(table,['runner.name,event_runner.date'],condition=cond({'event_runner.eid':eid}))

    runners.sort(key=lambda runner: date.toDatetime(runner[1]))

    reply = '七夕环西湖玫瑰跑\n\n不给情人买玫瑰，High去西湖跑玫瑰\n\n集合地点：{}\n集合时间：{}\n'.format('少年宫旗杆下','08-18(周六)07:00')
    for i in range(len(runners)):
        reply = reply + '{}. {}'.format(i+1,runners[i][0])
    
    return reply


def event(name):
    events = store.query('event',['*'],condition=cond({'name':name}))
    if not none_or_empty(events) and len(events) > 0:
        return events[0]
    return None

def help_reply(display,text):
    # #qi 齐队牌鸡汤
    # 姓名只需初始化一次，再次出现视为修改
    # 累计、计划每月只需初始化一次，再次出现视为修改
    # 初始化后每天打卡只需：#run日跑，如#run5
    # 支持每天打卡一次，再次打卡视为修改
    # #run5 当天打卡5公里，累计自动累加5
    # #run5/10 当天打卡5公里，设定累计10公里
    # #run5/10/60 当天打卡5公里，设定累计10公里，设定本月计划60公里
    return  '''
    格式：#run[姓名]日跑[/累计][/计划]
    如： #run张三5/10/60
    #run0 撤销当天打卡记录
    #run0.01 不跑步也可打卡
    #rose 报名七夕玫瑰跑，再次输入撤销报名
    #motto箴言 增加跑步箴言，将随机展示
    #help 查看本帮助
    '''

def run(display,name,data):
    logger.debug('receive name - {}, data - {}'.format(name,data))
    if not none_or_empty(name):
        update_name(display,name)


    if(len(data)>0):
        update_distance(display,data)

def realtime_reply():
    #按照总跑距排序
    text = rank_reply('total')
    logger.debug('realtime reply: %s' % text)
    return text

def concludsion_reply():
    text = rank_reply('distance')
    logger.debug('conclusion reply: %s' % text)
    return text

def rank_reply(order,reverse=True):
    reply = header()
    marks = rank(order=order,reverse=reverse)

    for i in range(len(marks)):
        mark = marks[i]
        reply = reply + '{}. {} {}/{}/{}\n'.format(i+1,mark['name'],format_number(mark['distance']),format_number(mark['total']),format_number(mark['plan']))
    
    return reply

def format_number(number):
    if none_or_empty(number):
        return ''
    if '.' in str(number):
        return '%.1f' % number
    return str(number)
    
def header():
    day = date.date()
    month = date.month()

    head = '{} {}\n\n'.format(day,room)
    head = head + '{}\n\n'.format(motto())
    head = head + '日跑量/{}月累计/{}月计划\n'.format(month,month)

    return head

def motto():
    if not none_or_empty(today_motto):
        return '{} - \n{}'.format('齐队',today_motto)
    
    count = store.count('motto')

    if count == None or count == 0:
        return mottos[random.randint(0,len(mottos)-1)]
    
    max_id = store.value('motto','max(id)')
    random_motto = store.query('motto',['content','rid'],cond({'id':random.randint(1,max_id)}))

    if random_motto == None:
        return mottos[random.randint(0,len(mottos)-1)]
    
    random_motto=random_motto[0]
    content = random_motto[0]
    rid = random_motto[1]
    name = store.value('runner','name',cond({'id':rid}))

    return '{} - \n{}'.format(name,content)

def rank(order='time',reverse=False):
    table_runner = 'runner'
    table_record = 'record'
    table_plan = 'plan'

    day = date.date()
    year = date.year()
    month = date.month()

    condition = cond({'date':day})

    records = store.query(table_record,['rid','distance','time'],condition=condition)
    marks = []
    for record in records:
        id = record[0]
        distance = record[1]
        time = record[2]
        name = store.value(table_runner,'name',condition=cond({'id':id}))
        total = 0
        plan = 0
        plans = store.query(table_plan,['plan','total'],condition=cond({'rid':id,'year':year,'month':month}))
        if plans and len(plans) > 0:
            plans = plans[0]

        if plans:
            plan = plans[0]
            total = plans[1]
        
        mark = {'name':name,'distance':distance,'total':total,'plan':plan,'time':date.toTime(time)}
        marks.append(mark)
    
    marks.sort(reverse=reverse,key= lambda mark:mark[order])
    return marks

def extra_run(text):
    reg = r'[\d+\.?\d+/?]*'
    records = re.findall(reg,text)
    logger.debug('match data: %s' % records)
    for record in records:
        if none_or_empty(record):
            continue
        else:
            name = text[0:text.index(record)].strip()
            cols = record.split('/')
            for col in cols:
                if col=='':
                    cols.remove(col)
            logger.debug('extra run data: %s' % [name,cols] )
            return name,cols
    return None


#刷新跑团成员列表
def update_members(chatroom):
    global room
    room = chatroom
    chatroom  = itchat.search_chatrooms(name=room)
    room_id = chatroom[0]['UserName']
    memberList = itchat.update_chatroom(room_id, detailedMember=True)['MemberList']

    for member in memberList:
        update_display(member['NickName'],member['DisplayName'])

#刷新群成员备注名，若不存在就新建
def update_display(nick,display,remark=None):
    table = 'runner'
    if display == None or display == '':
        display = nick
    name = display

    condition = cond({'nick':nick})
    if not update_or_insert(table,['nick','name','remark','display'],[nick,name,remark,display],condition):
        id = store.value(table,'id',condition=condition)
        update_plan(id,60)

#刷新成员真实姓名
def update_name(display,name):
    condition = cond({'display':display})
    update('runner','name',name,condition)

def update_distance(display,cols):
    if not validate(cols):
        return

    condition = cond({'display':display})
    rid = store.value('runner','id',condition=condition)


    distance = cols[0]
    record = None
    #撤回功能
    if(distance == 0):
        delete_record(rid)
    else:
        record = update_record(rid,distance)

    total = None if len(cols) < 2 else cols[1]
    if total:
        update_total(rid,total)
    else:
        if not none_or_empty(record): #如果已经打卡，则进行纠正
            old = record[0]
            new = record[1]
            distance = new - old
        update_total(rid,distance,add=True)
    
    plan = None if len(cols) < 3 else cols[2]
    if plan:
        update_plan(rid,plan)

def validate(cols):
    
    global error
    for i in range(len(cols)):
        col = isNumber(cols[i])
        if not none_or_empty(col):
            cols[i] = col
        else:
            error = '打卡格式不正确'
            return False
    logger.debug('convert to float: %s' % cols)
    if len(cols)>1:
        if cols[1] < cols[0]:
            error = '累计跑距不得小于今日跑距'
            return False
    

    return True

def runner(display):
    table = 'runner'

    condition = cond({'display':display})

    runner = store.query(table,['id','name','nick'],condition)

    if not none_or_empty(runner) and len(runner)>0:
        runner = runner[0]
        return (runner[0],runner[1],runner[2])
    return None

def isNumber(str):
    try:
        n = float(str)
        return n
    except ValueError:
        return None


def delete_record(rid):
    table = 'record'
    day = date.date()
    condition = cond({'rid':rid,'date':day})

    old = store.value(table,'distance',condition=condition)
    if not none_or_empty(old):
        update_total(rid,old*(-1),add=True)
        store.delete(table,condition=condition)
    

#刷新或者新建当日跑步记录
def update_record(rid,distance):
    day = date.date()
    now = date.now()
    condition = cond({'rid':rid,'date':day})
    table = 'record'
    return update_or_insert(table,['rid','date','time','distance'],[rid,day,now,distance],condition)

#刷新或新建当月跑步累计里程
def update_total(rid,total,add=False):
    table = 'plan'
    year = date.year()
    month = date.month()
    condition = cond({'rid':rid,'year':year,'month':month}) 

    if add:
        old = store.value(table,'total',condition=condition)
        if old:
            total = total + old

    return update_or_insert(table,['rid','year','month','total'],[rid,year,month,total],condition)

#刷新或新建当月计划里程
def update_plan(rid,plan):
    table = 'plan'
    year = date.year()
    month = date.month()
    condition = cond({'rid':rid,'year':year,'month':month}) 
    return update_or_insert(table,['rid','year','month','plan'],[rid,year,month,plan],condition)

def update_or_insert(table,fields,values,condition):
    field=fields[-1]
    value = values[-1]
    up = update(table,field,value,condition)
    if not none_or_empty(up):
        return up
    else:
        store.insert(table,fields,[values])
        logger.debug('insert %s: %s' % (table,values))
        return None


def update(table,field,value,condition):
    if store.exists(table,condition):
        old = store.value(table,field,condition=condition)
        if old !=value:
            store.update(table,[field],[value],condition=condition)
            logger.debug('update %s: %s=%s' % (table,field,value))
        return (old,value)
    return None 

#根据字典生成查询条件
def cond(dict):
    keys = list(dict.keys())
    key = keys[0]
    condition = "%s='%s'" % (key,dict[key])

    for key in keys[1:]:
        condition = condition + ' and ' + ("%s='%s'" % (key,dict[key]))
    return condition
def none_or_empty(str):
    return str==None or str==''




    
