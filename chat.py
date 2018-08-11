import itchat
import store
import sys
import record

from log import Logger
logger = Logger(__name__).log()

def login(hotReload=True,qrCallback=None,loginCallback=None):
    itchat.auto_login(hotReload = hotReload,qrCallback=qrCallback,loginCallback=loginCallback)
    itchat.run(debug=True,blockThread=True)

def logout():
    itchat.logout()

@itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
def text_reply(msg):
    response = record.reply(msg)
    if not record.none_or_empty(response):
        return msg.user.send(response)
        #print(response)

if __name__=='__main__':

    if len(sys.argv)<2:
        logger.debug('请指定群聊名称')
        sys.exit(1)
    
    room = sys.argv[1].strip()
    
    store.init()
    itchat.auto_login()
    record.update_members(room)

    itchat.run(debug=True,blockThread=True)

    

    # text='#run分结束啦20.3/49.3/150.3'
    # keys = extra(text)


    # text='#run得劲20.3/49.3/150.3'
    # keys = extra(text)


    # text='#的分结束啦20.3/ / /'
    # keys = extra(text)




    
