#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Frank.Wu'

"""
Author:Frank.Wu
Date:2018-12-16
version:1.0.0
email:wuwei_cug@163.com
github:https://github.com/RemoteSensingFrank
Desc: Using MongoDB GFS to store and restore big file\
      the GFS using chunk to split the file into chunks\
      and by the way I though the procedures is like:\
      1.Receive the data from the client;\
      2.Store the data into the file system;\
      3.Put the data into the GFS;\
      4.Delete the data in the filesystem\
      So what we considerd is how to put the file into the GFS in filesystem
"""
#encoding=utf-8
#sys
import json
import os
import hashlib
import  threading
import sys
import StringIO

import pymongo
import bson
from gridfs import *
from PIL import Image

import log as log
import instance as instance

#global params
configure   = instance.conf
logLock     = threading.Lock()
"""
used to operate the file store in GridFS
for a large file it's necessary to create
a new thread the upload and delete
"""
class GFS:
    #initial GFS operation class
    #connect to mongoDB
    def __init__(self, *args, **kwargs):
        try:
            host=configure.get("GFS", "db_host")
            port=configure.get("GFS", "db_port")
            db  =configure.get("GFS", "db_db")

            self.client=pymongo.MongoClient(str(host),int(port))
            if(db is not None):
                dbList = self.client.database_names()
                if(db not in dbList):
                    log.logger.warning("database don't existed and create a new database")
                self.db    =self.client[db]
            self.fsys = GridFS(self.db)
            if self.fsys is None:
                log.logger.error('cannot create GFS collection')
        except:
            log.logger.error("mongo db connection failed!")
    
    #close the connection
    def __del__(self):
        try:
            self.client.close()
            self.client=None
            self.db=None
            self.fsys=None
            log.logger.info('disconnect GridFS success')
        except:
            log.logger.error('disconnect GridFS error')

    #store file into mongoDB
    #param objFile:file object or binnary string
    #param filename:file name
    def put(self,objFile,filename):
        #try:
        fileid=self.fsys.put(objFile,filename=filename)
        log.logger.debug('store file into the mongoDB')
        return fileid

    
    #delete file usting fileid
    #param fileid:file id
    def delete_id(self,fileid):
        try:
            log.logger.debug('delete file into monboDB')
            return self.fsys.delete(fileid)
        except:
            log.logger.error('delete file into the mongoDB error')
            return configure.get("return_info","mongo_GFS_delete_error")

    #delete file according to the filename
    #delete all version of the named file
    #param filename:file name
    def delete_name(self,filename):
        for grid_out in fsys.find({"filename": filename},
                no_cursor_timeout=True):
            fileid = outs[0]._id
            self.delete_id(fileid)

#create a new Thread to Put file into the 
def AttachFileThread(path,filename):
    try:
        gfsOpt = GFS()
        with open(path,'rb') as objFile:
            fileid=gfsOpt.put(objFile,filename)

            #lock the log to in case of write confuse log
            logLock.acquire()
            log.logger.debug('store file success')
            os.remove(path)
            logLock.release()
    except:
        log.logger.error('store file error')

#create a new Thread to Del file in the MongoDB
def DeleteFileThread(filename):
    try:
        gfsOpt = GFS()
        for grid_out in fsys.find({"filename": filename},
                        no_cursor_timeout=True):
            gfsOpt.delete_name

        #lock the log to in case of write confuse log
        logLock.acquire()
        log.logger.debug('store file success')
        logLock.release()
    except:
        log.logger.error('store file error')


#used to create thumbnail for image files
#image size of the thumbnail is smaller than(300,200)
def ImageFileThumbnail(infoJson):
    #TODO: Resize the image file
    return configure.get("return_info","success")    

"""
used to operate the file with the attachments
the base database only store the information of the 
file info and the attachment is stored into the GridFS
connect with the GridFS and file info using file name
to reduce the length of the file name we hash code the 
file name using sha1
"""
class DBFileAttach:
    #using information to connection the collection
    def __init__(self):
        try:
            host=configure.get("mongo_info", "db_host")
            port=configure.get("mongo_info", "db_port")
            db  =configure.get("mongo_info", "db_db")
            collection  =configure.get("mongo_info", "db_collection")
            self.client=pymongo.MongoClient(str(host),int(port))
            if(db is not None):
                dbList = self.client.database_names()
                if(db not in dbList):
                    log.logger.warning("database don't existed and create a new database")
                self.db    =self.client[db]
            if collection is not None:
                collectionList = self.db.collection_names()
                if(collection not in dbList):
                    log.logger.warning("collection don't existed and create a new collection")
                self.collection=self.db[collection]
        except:
            log.logger.error("mongo db connection failed!")

    #connect to the database
    #param dbname:database name
    def connDatabase(dbname):
        assert self.client is not None
        try:
            dbList = self.client.database_names()
            if(db not in dbList):
                log.logger.warning("database don't existed and create a new database")
            self.db    =self.client[db]
            return configure.get("return_info","success")
        except:
            log.logger.error('connect to database failed')

    #connect to the collection
    #param collection:collection name
    def connCollection(collection):
        assert self.db is not None
        try:
            collectionList = self.client.collection_names()
            if(collection not in collectionList):
                log.logger.warning("collection don't existed and create a new collection")
            self.collection    =self.client[collection]
            return configure.get("return_info","success")
        except:
            log.logger.error('connect to collection failed')

    #list all the collections of the database
    def getCollectionListsInfo(self):
        assert self.db is not None
        collectionList = self.db.list_collection_names()
        return json.dumps(collectionList)

    #insert file data into filedata database using GFS to store the data
    #param infoJson:json info of the file
    #param gfsinstance:database to store the file
    #param collection:collection to store the file
    #param func: user defined process
    def insertFileAttach(self,infoJson,func=None):
        path=infoJson['file_attach_path']
        uploadpath = infoJson['upload_path']
        #hashcode for path
        sha1 = hashlib.sha1()
        sha1.update(uploadpath.encode('utf-8'))
        hashPath = sha1.hexdigest()
        
        #file data stored by GFS
        try:
            t=threading.Thread(target=AttachFileThread,args=(path,hashPath))
            t.setName("add file"+os.path.basename(path)+"into mongoDB")
            #t.setDaemon(True)
            if(func!=None):
                func(infojson)
            #file info stored by mongoDB
            self.collection.insert_one(infoJson)
            t.start()
            return configure.get("return_info","success")
        except Exception:
            log.logger.error('insert into database failed')


    #delete file stored in the mongoDB
    #param infoJson:json info of the file
    #param fileDataDB:database to store the file
    #param collection:collection to store the file
    def deleteFile(self,infoJson):
        try:
            path=infoJson['file_attach_path']
            uploadpath = infoJson['upload_path']
            #hashcode for path
            sha1 = hashlib.sha1()
            sha1.update(uploadpath.encode('utf-8'))
            hashPath = sha1.hexdigest()
            self.collection.delete_one(infoJson)
            t=threading.Thread(target=DeleteFileThread,args=(hashPath))
            t.setName("delete "+os.path.basename(path)+" from mongoDB")
            t.start()
            return configure.get("return_info","success")
        except KeyError:
            log.logger.error('value of the key does not existed please check the input data')
        except NameError:
            log.logger.error('error of none data')



"""
used to operate the small file directly read the file
as the binnary data and store the file as base64 object
into the mongoDB
"""
class DBFileObject:
    #using information to connection the collection
    def __init__(self):
        try:
            host=configure.get("mongo_info", "db_host")
            port=configure.get("mongo_info", "db_port")
            db  =configure.get("mongo_info", "db_db")
            collection  =configure.get("mongo_info", "db_collection")
            self.client=pymongo.MongoClient(str(host),int(port))
            if(db is not None):
                dbList = self.client.database_names()
                if(db not in dbList):
                    log.logger.warning("database don't existed and create a new database")
                self.db    =self.client[db]
            if collection is not None:
                collectionList = self.db.collection_names()
                if(collection not in dbList):
                    log.logger.warning("collection don't existed and create a new collection")
                self.collection=self.db[collection]
        except:
            log.logger.error("mongo db connection failed!")

    #connect to the database
    #param dbname:database name
    def connDatabase(dbname):
        assert self.client is not None
        try:
            dbList = self.client.database_names()
            if(db not in dbList):
                log.logger.warning("database don't existed and create a new database")
            self.db    =self.client[db]
            return configure.get("return_info","success")
        except:
            log.logger.error('connect to database failed')

    #connect to the collection
    #param collection:collection name
    def connCollection(collection):
        assert self.db is not None
        try:
            collectionList = self.client.collection_names()
            if(collection not in collectionList):
                log.logger.warning("collection don't existed and create a new collection")
            self.collection    =self.client[collection]
            return configure.get("return_info","success")
        except:
            log.logger.error('connect to collection failed')

    #list all the collections of the database
    def getCollectionListsInfo(self):
        assert self.db is not None
        collectionList = self.db.list_collection_names()
        return json.dumps(collectionList)

    #insert file data into filedata database using GFS to store the data
    #param infoJson:json info of the file
    #param gfsinstance:database to store the file
    #param collection:collection to store the file
    #param func: user defined process
    def insertFileAttach(self,fileObj,infoJson,func=None):
        #file data stored by binnarg obj
        try:
            fileContent = StringIO(fileObj.read())
            infoJson["fileobject"]= bson.binary.Binary(content.getvalue())
            if(func!=None):
                func(infojson)
            #file info stored by mongoDB
            self.collection.insert_one(infoJson)
            return configure.get("return_info","success")
        except Exception:
            log.logger.error('insert into database failed')

    #delete file stored in the mongoDB
    #param infoJson:json info of the file
    #param fileDataDB:database to store the file
    #param collection:collection to store the file
    def deleteFile(self,infoJson):
        try:
            self.collection.delete_one(infoJson)
            return configure.get("return_info","success")
        except KeyError:
            log.logger.error('value of the key does not existed please check the input data')
        except NameError:
            log.logger.error('error of none data')

