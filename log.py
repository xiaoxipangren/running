
import logging

#coding=utf-8
class Logger():
    def __init__(self,logger):
 
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
 
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler('log.txt')
        fh.setLevel(logging.DEBUG)
 
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
 
        # 定义handler的输出格式    
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s-[%(filename)s:%(lineno)d]')
        fh.setFormatter(log_format)
        ch.setFormatter(log_format)
 
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
   
    def log(self):
        return self.logger