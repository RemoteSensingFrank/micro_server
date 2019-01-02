#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Frank.Wu'

"""
Author:Frank.Wu
Date:2018-12-16
version:1.0.0
email:wuwei_cug@163.com
github:https://github.com/RemoteSensingFrank
Desc: Using file system to store and restore files\
      if the username and password are provided\
      first login to the share directory and read and write\
      file to the shared directory.
"""
#encoding=utf-8
#sys
import os
import sys

sys.path.append('../')

import src.log as log
import src.instance as instance

#global params
configure   = instance.conf
"""
fileIO warpper: first mapping the shared folder \
                then create file with relative path
"""
class FileIOEx:
    #create the net connect
    def __init__(self, *args, **kwargs):
        try:
            self.local=False
            shared_dir = configure.get("shared","shared_path")
            username   = configure.get("shared","shared_user")
            password   = configure.get("shared","shared_psw")
            if(shared_dir==""):
                self.local=True
                log.logger.info("using local folder")
            elif(username=="" or password==""):
                os.system(r'net use tmp:\\'+shared_dir)
                log.logger.info("connect to folder success and mapping the folder to tmp:\\")
            else:
                os.system(r'net use tmp:\\'+shared_dir+"$"+"\""+password+"\" "+"/USER:"+username)
                log.logger.info("connect to folder success and mapping the folder to tmp:\\")
        except:
            log.logger.error("connect to folder failed!")

    #open file in shared directory
    #param path:relative path if connect to shared folder\
    #           abs path if connect to local folder
    def open(self,path,opt):
        try:
            pathEx=""
            if(self.local is not True):
                pathEx=os.path.join("tmp:\\",path)
            else:
                pathEx= path
            dirPath=os.path.dirname(pathEx)
            if(os.path.exists(dirPath) is not None):
                os.makedirs(dirPath)

            fobj = open(pathEx,opt)
            return fobj
        except:
            log.logger.error("open or create file failed")
            return None

    #remove the file of the path
    #param path:file path to be removed
    def remove(self,path):
        try:
            pathEx=""
            if(self.local is not True):
                pathEx=os.path.join("tmp:\\",path)
            else:
                pathEx= path
            dirPath=os.path.dirname(pathEx)
            os.remove(pathEx)
        except:
            log.logger.error("open or create file failed")
            return None

    #get file size
    def size(self,path):
        try:
            pathEx=""
            if(self.local is not True):
                pathEx=os.path.join("tmp:\\",path)
            else:
                pathEx= path
            return os.path.getsize(pathEx)
        except:
            log.logger.error("get file size failed")
            return -1

    #save the file object to the path
    #param fileObj:file object to be saved
    #param path   :file saved path
    def save(self,fileObj,path):
        try:
            pathEx=""
            if(self.local is not True):
                pathEx=os.path.join("tmp:\\",path)
            else:
                pathEx= path
            dirPath=os.path.dirname(pathEx)
            log.logger.error("saved the file success")
            fileObj.save(pathEx)
        except:
            log.logger.error("failed to save the file")
            return None