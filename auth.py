import itchat
import re
import store
import date
import random

from log import Logger

test_room='test'
runing_club='珞珈跑团'
mark = '#run'

help = '#help'

mottos=[
    '奔跑吧，大胸弟',
    'just do running',
    '当你跑步时，你在想村上春是哪种树'
    '我是奔跑的五花肉，我为自己带盐',
    '跑步是为了更愉快的喝酒',
    '我跑故我在',
    'RUN,GUMP,RUN!',
    '已离家Five hundred miles，我该怎么回去'
]

room = test_room # runing_club

logger = Logger(__name__).log()

def login(hotReload=True,qrCallback=None,loginCallback=None):
    itchat.auto_login(hotReload = hotReload,qrCallback=qrCallback,loginCallback=loginCallback)
    itchat.run(debug=True,blockThread=True)

def logout():
    itchat.logout()

@itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
def text_reply(msg):
    response = reply(filter_contact,msg)
    if not none_or_empty(response):
        return msg.user.send(response)
        #print(response)

def reply(filter_fn,msg):
    logger.debug('receive message: %s' % msg)
    result = filter_fn(msg)
    if not result:
        return None

    else:
        text = msg['Text'].strip()
        logger.debug('receive text: %s' % text)

        if(text.startswith(mark)):
            text = text.replace(mark,'').strip()
            # if '章波' in text:
            #     return '章波是个大沙皮'
            # if '东清' in text:
            #     return '东哥是个大逗比'
            data = extra(text)
            
            if data:
                name = data[0]
                cols = data[1]

                display = msg['ActualNickName']
                record(display,name,cols)
                #考虑增加使用名字作为识别标志进行他人辅助打卡功能

            return realtime_reply()
        elif(text.startswith(help)):
            return help_reply()
def help_reply():
    return  '''
    打卡新选择 跑步很简单

    格式：#run[姓名]日跑[/累计][/计划]
    如： #run郑海青5/10/60
    姓名只需初始化一次，再次出现视为修改
    累计、计划每月只需初始化一次，再次出现视为修改
    初始化后每天打卡只需：#run日跑，如#run5
    支持每天打卡一次，再次打卡视为修改

    #run5 当天打卡5公里，累计自动累加5
    #run5/10 当天打卡5公里，设定累计10公里
    #run5/10/60 当天打卡5公里，设定累计10公里，设定本月计划60公里
    #help 查看本帮助
    
    通过群昵称追踪身份，请谨慎修改群昵称
    '''

def record(display,name,data):
    if not none_or_empty(name):
        update_name(display,name)

    if(len(data)>0):
        update_distance(display,data)

def realtime_reply():
    text = rank_reply('time')
    logger.debug('realtime reply: %s' % text)
    return text

def concludsion_reply():
    text = rank_reply('distance')
    logger.debug('conclusion reply: %s' % text)
    return text

def rank_reply(order):
    reply = header()
    marks = rank(order=order)

    for i in range(len(marks)):
        mark = marks[i]
        reply = reply + '{}. {} {}/{}/{}\n'.format(i+1,mark['name'],mark['distance'],mark['total'],mark['plan'])
    
    return reply


def header():
    day = date.date()
    month = date.month()

    head = '{} {}\n\n'.format(day,room)
    head = head + '{}\n\n'.format(mottos[random.randint(0,len(mottos)-1)])
    head = head + '日跑量/{}月累计/{}月计划\n'.format(month,month)

    return head



def rank(order='time'):
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
    
    marks.sort(key= lambda mark:mark[order])
    return marks

def extra(text):
    reg = r'[\d./]*'
    records = re.findall(reg,text)
    for record in records:
        if re.match(r'\d\.|/',record)!=None or none_or_empty(record):
            continue
        else:
            name = text[0:text.index(record)].strip()
            cols = record.split('/')
            for col in cols:
                if col=='':
                    cols.remove(col)
            logger.debug('extra data: %s' % [name,cols] )
            return name,cols
    return None



def filter_contact(msg):
    from_user = msg['User']['NickName']
    if(from_user!=room):
        return False
    return True

#刷新跑团成员列表
def update_members():
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
    condition = cond({'display':display})
    rid = store.value('runner','id',condition=condition)


    distance = float(cols[0])

    #撤回功能
    if(distance == 0):
        delete_record(rid)
    else:
        record = update_record(rid,distance)

    total = None if len(cols) < 2 else float(cols[1])
    if total:
        update_total(rid,total)
    else:
        if not none_or_empty(record): #如果已经打卡，则进行纠正
            old = record[0]
            new = record[1]
            distance = new - old
        update_total(rid,distance,add=True)
    
    plan = None if len(cols) < 3 else float(cols[2])
    if plan:
        update_plan(rid,plan)

def delete_record(rid):
    table = 'record'
    day = date.date()
    condition = cond({'rid':rid,'date':day})
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
    return str==None or str=='' or len(str) == 0

if __name__=='__main__':
    store.init()
    itchat.auto_login()
    
    update_members()


    itchat.run(debug=True,blockThread=True)

    

    # text='#run分结束啦20.3/49.3/150.3'
    # keys = extra(text)


    # text='#run得劲20.3/49.3/150.3'
    # keys = extra(text)


    # text='#的分结束啦20.3/ / /'
    # keys = extra(text)




    
