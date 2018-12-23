#coding=utf-8
__author__ = 'Frank.Wu'

"""
log configure
"""
import logging
import logging.handlers
import datetime
import os

logger = logging.getLogger("mlserver")
logger.setLevel(logging.DEBUG)

#all log info 
all_handler = logging.handlers.TimedRotatingFileHandler('../data/log/all.log',when='midnight',
            interval=7,backupCount=5,atTime=datetime.time(0,0,0,0))
all_handler.setFormatter(logging.Formatter("%(asctime)s-%(levelname)s-%(message)s"))


#error log info
err_handler = logging.handlers.TimedRotatingFileHandler('../data/log/err.log',when='midnight',
            interval=30,backupCount=5,atTime=datetime.time(0,0,0,0))
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(logging.Formatter("%(asctime)s-%(levelname)s-%(message)s"))

#print log on the screen
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s-%(levelname)s-%(message)s"))

#add handler
logger.addHandler(all_handler)
logger.addHandler(err_handler)
logger.addHandler(console_handler)
        