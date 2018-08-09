ssh aliyun 'mkdir chatroom'

scp -r . aliyun:chatroom/

ssh aliyun 'rm -rf /var/www/wechat/chatroom/*'
ssh aliyun 'mv chatroom/* /var/www/wechat/chatroom'
ssh aliyun 'rm -rf chatroom'