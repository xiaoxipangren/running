import itchat
import re
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

def reply(filter_fn,msg):
    logger.debug(msg)
    result = filter_fn(msg)
    if not result:
        return None

    else:
        text = msg['Text']
        logger.debug('receive text: %s' % text)


        if(text.startswith(mark)):
            text = text.replace(mark,'').strip()
            data = extra(text)
            print(data)
            return '您输入了话题： %s' % text

def extra(text):
    reg = '[\d./]*'
    records = re.findall(reg,text)
    print(records)
    for record in records:
        if re.match('\d\.|/',record)!=None or record == '' or len(record) == 0:
            continue
        else:
            name = text[0:text.index(record)].strip()
            cols = record.split('/')
            for col in cols:
                if col=='':
                    cols.remove(col)
            print(name,cols)
            return name,cols
    return None



def filter_contact(msg):
    from_user = msg['User']['NickName']

    if(from_user!=test_room):
        return False
    return True

@itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
def text_reply(msg):
    response = reply(filter_contact,msg)
    if response!=None:
        return msg.user.send(response)



if __name__=='__main__':
    itchat.auto_login()
    itchat.run(debug=True,blockThread=True)

    # text='#run分结束啦20.3/49.3/150.3'
    # keys = extra(text)


    # text='#run得劲20.3/49.3/150.3'
    # keys = extra(text)


    # text='#的分结束啦20.3/ / /'
    # keys = extra(text)




    
