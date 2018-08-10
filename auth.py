import itchat
import re
import store
import date

from log import Logger

test_room='test'
runing_club='珞珈跑团'
mark = '#run'

logger = Logger(__name__).log()

def login(hotReload=True,qrCallback=None,loginCallback=None):
    itchat.auto_login(hotReload = hotReload,qrCallback=qrCallback,loginCallback=loginCallback)
    itchat.run(debug=True,blockThread=True)

def logout():
    itchat.logout()

@itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
def text_reply(msg):
    response = reply(filter_contact,msg)
    if response!=None:
        return msg.user.send(response)

def reply(filter_fn,msg):
    logger.debug('receive message: %s' % msg)
    result = filter_fn(msg)
    if not result:
        return None

    else:
        text = msg['Text']
        logger.debug('receive text: %s' % text)

        if(text.startswith(mark)):
            text = text.replace(mark,'').strip()
            data = extra(text)
            
            if data:
                name = data[0]
                cols = data[1]

                display = msg['ActualNickName']
                
                if name != None:
                    update_name(display,name)

                if(len(cols)>0):
                    update_distance(display,cols)

            return '您输入了话题： %s' % text


def extra(text):
    reg = r'[\d./]*'
    records = re.findall(reg,text)
    for record in records:
        if re.match(r'\d\.|/',record)!=None or record == '' or len(record) == 0:
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
    if(from_user!=test_room):
        return False
    return True

#刷新跑团成员列表
def update_members():
    club = '珞珈跑团'
    chatroom  = itchat.search_chatrooms(name=club)
    room_id = chatroom[0]['UserName']
    memberList = itchat.update_chatroom(room_id, detailedMember=True)['MemberList']

    for member in memberList:
        update_display(member['NickName'],member['DisplayName'])

#刷新群成员备注名，若不存在就新建
def update_display(nick,display,remark=None):
    table = 'runner'
    if display == None:
        display = nick
    name = display

    condition = cond({'nick':nick})
    update_or_insert(table,['nick','name','remark','display'],[nick,name,remark,display],condition)

#刷新成员真实姓名
def update_name(display,name):
    condition = cond({'display':display})
    update('runner','name',name,condition)

def update_distance(display,cols):
    condition = cond({'display':display})
    runner = store.query('runner',['id','name','display'],condition=condition)
    rid = runner[0]

    distance = cols[0]
    update_record(rid,distance)

    total = None if len(cols) < 2 else cols[1]
    if total:
        update_total(rid,total)
    plan = None if len(cols) < 3 else cols[2]
    if plan:
        update_plan(rid,plan)

#刷新或者新建当日跑步记录
def update_record(rid,distance):
    day = date.date()
    now = date.now()
    condition = cond({'rid':rid,'date':day})
    table = 'runner'
    update_or_insert(table,['rid','date','time','distance'],[rid,day,now,distance],condition)

#刷新或新建当月跑步累计里程
def update_total(rid,total):
    table = 'plan'
    year = date.year()
    month = date.month()
    condition = cond({'rid':rid,'year':year,'month':month})    
    update_or_insert(table,['rid','year','month','reald'],[rid,year,month,total],condition)

#刷新或新建当月计划里程
def update_plan(rid,plan):
    table = 'plan'
    year = date.year()
    month = date.month()
    condition = cond({'rid':rid,'year':year,'month':month}) 
    update_or_insert(table,['rid','year','month','pland'],[rid,year,month,plan],condition)

def update_or_insert(table,fields,values,condition):
    field=fields[-1]
    value = values[-1]
    if update(table,field,value,condition):
        pass
    else:
        store.insert(table,fields,[values])
        logger.debug('insert %s: %s' % (table,values))

def update(table,field,value,condition):
    if store.exists(table,condition):
        model = store.query(table,[field],condition=condition)
        if model[0][0] !=value:
            store.update(table,[field],[value],condition=condition)
            logger.debug('update %s: %s=%s' % (table,field,value))
        return True
    return False 

#根据字典生成查询条件
def cond(dict):
    keys = list(dict.keys())

    condition = "%s='%s'" % (keys[0],dict[keys[0]])

    for key in keys[1:]:
        condition = condition + ' and ' + ("%s='%s'" % (key,dict[key]))
    return condition


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




    
