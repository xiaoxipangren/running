
import logging

#coding=utf-8
class Logger():
    def __init__(self,logger):
 
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
 
        fh = logging.FileHandler('log.txt')
        fh.setLevel(logging.DEBUG)
 
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
 
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s-[%(filename)s:%(lineno)d]')
        fh.setFormatter(log_format)
        ch.setFormatter(log_format)
 
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
   
    def log(self):
        return self.logger