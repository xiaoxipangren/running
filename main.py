import chat
import os 
import itchat

from log import Logger
from socketserver import ThreadingTCPServer, StreamRequestHandler


logger = Logger(__name__).log()
qr = 'qr.jpg'
qr_dir = '/home/zhenghq/python/running/chatroom'

if not os.path.exists(qr_dir):
    os.makedirs(qr_dir)

class Handler(StreamRequestHandler):  
    def handle(self):  

        command = str(self.request.recv(10240),'utf-8')  
          
        if(command == 'login'):  
            self.login()
        elif(command == 'logout'):  
            pass  
        else:  
            pass
    def login(self):  
        logger.debug('login request')
        def qrCallback(uuid,status,qrcode):
            '''
                 status 0－初始请求，200-扫码成功,408－二维码过期
            '''
            status = int(status)
            if status == 0:
                qr_file = os.path.join(qr_dir,qr)
                with open(qr_file,'wb') as png:
                    png.write(qrcode)
                logger.debug('download qrcode to '+qr_file)
                self.request.sendall(bytes(qr_file,'utf-8'))

        chat.login(hotReload=False,qrCallback=qrCallback)


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    return msg.text


if __name__ == "__main__":  
    HOST, PORT = "localhost", 9999  

    logger.debug('Server listening on %s:%d ......' % (HOST,PORT))
    logger.debug('Press Ctrl+C to quit')


    server = ThreadingTCPServer((HOST, PORT), Handler)  
 
    server.serve_forever()  
    
    
