import itchat
import re
from log import Logger

test_room='test'
runing_club='珞珈跑团'

logger = Logger(__name__).log()

def login(hotReload=True,qrCallback=None,loginCallback=None):
    itchat.auto_login(hotReload = hotReload,qrCallback=qrCallback,loginCallback=loginCallback)
    itchat.run(debug=True,blockThread=True)

def logout():
    itchat.logout()

def reply(filter_fn,msg):
    result = filter_fn(msg)
    if not result:
        logger.debug(msg)
        return None

    else:
        text = msg['Text']
        logger.debug('receive text: %s' % text)

        if(text.startswith('#')):
            return '您输入了话题： %s' % text

def extra(text):
    reg = '(\d*.?\d+)/?'
    keywords = re.findall(reg,text)
    return keywords



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
    # itchat.auto_login()
    # itchat.run(debug=True,blockThread=True)

    text='1.分结束啦20.3/49.3/150.3'
    keys = extra(text)
    print(keys)



    
