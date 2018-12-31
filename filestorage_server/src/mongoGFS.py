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

Date:2018-12-29
version:1.1.0
email:wuwei_cug@163.com
Add the large and small file storage and download

"""
#encoding=utf-8
#sys
import json
import os
import hashlib
import  threading
import sys
from io import BytesIO

import pymongo
import bson
from bson.objectid import ObjectId

from gridfs import *
from PIL import Image
sys.path.append('../')
import src.log as log
import src.instance as instance

#global params
configure   = instance.conf
logLock     = threading.Lock()
"""
used to operate the file store in GridFS
for a large file it's necessary to create
a new thread the upload and delete
"""

#using yield to make chunk
#param fileObj : must have read method
def download_file_chunkMongo(fileObj,length):
    while True:
        chunk = fileObj.read(20 * 1024 * 1024)  # 每次读取20M
        if not chunk:
            break
        progress=float(fileObj.tell()/length)
        yield chunk


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

    #download file with file id
    #param fileid:file id
    def download(self,fileid):
        try:
            """test~ error with do not import ObjectId from bson fixed
            filefind = self.fsys.find({"_id":ObjectId("5c22f47fe991a63eccbd7601")})
            for item in filefind:
                print(item) 
            """
            fileObj = self.fsys.get(ObjectId(fileid))
            for chunk in download_file_chunkMongo(fileObj,fileObj.length):
                yield chunk
        except:
            log.logger.error('cannot find file object')
            return configure.get("return_info","mongo_GFS_download_error")
    
    #return file object
    def download_send(self,fileid):
        try:
            fileObj = self.fsys.get(ObjectId(fileid))
            return fileObj
        except:
            log.logger.error('cannot find file object')
            return configure.get("return_info","mongo_GFS_download_error")


    #delete file useing fileid
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

    #get file size useing fileid
    #param fileid:file id
    def filesize(self,fileid):
        fInfo = self.fsys.find_one(ObjectId(str(fileid)))
        return fInfo.length

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
                if(collection not in collectionList):
                    log.logger.warning("collection don't existed and create a new collection")
                self.collection=self.db[collection]
        except:
            log.logger.error("mongo db connection failed!")

    #close connection
    def __del__(self):
        try:
            self.client.close()
            self.client=None
            self.db=None
            self.collection=None
            log.logger.info('disconnect mongoDB')
        except:
            log.logger.error('disconnect mongoDB error')

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

    #down load the file stored in the mongoDB GridFS
    #param fileid:file id in mongoDB
    def downloadFileAttach(self,fileid):
        try:
            gfsOpt = GFS()
            return gfsOpt.download(fileid)
        except KeyError:
            log.logger.error('value of the key does not existed please check the input data')
        except NameError:
            log.logger.error('error of none data')
    
    #using send method to send file data so 
    #only to return the file object
    #param fileid：file id in mongoDB
    def downloadFileAttachSend(self,fileid):
        try:
            gfsOpt = GFS()
            return gfsOpt.download_send(fileid)
        except KeyError:
            log.logger.error('value of the key does not existed please check the input data')
        except NameError:
            log.logger.error('error of none data')
    

    #get the size of the attach file
    #param fileid: file id in mongoDB
    def getFileAttachSize(self,fileid):
        try:
            gfsOpt = GFS()
            return gfsOpt.filesize(fileid)
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
                if(collection not in collectionList):
                    log.logger.warning("collection don't existed and create a new collection")
                self.collection=self.db[collection]
        except:
            log.logger.error("mongo db connection failed!")

    #close connection
    def __del__(self):
        try:
            self.client.close()
            self.client=None
            self.db=None
            self.collection=None
            log.logger.info('disconnect mongoDB')
        except:
            log.logger.error('disconnect mongoDB error')

    #insert file data into filedata database using GFS to store the data
    #param infoJson:json info of the file
    #param gfsinstance:database to store the file
    #param collection:collection to store the file
    #param func: user defined process
    def insertFileObject(self,fileObj,infoJson,func=None):
        #file data stored by binnarg obj
        try:
            fileContent = BytesIO(fileObj.read())
            infoJson["fileobject"]= bson.binary.Binary(fileContent.getvalue())
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

    #down load the file stored in the mongoDB GridFS
    #param fileid:fileid
    def downloadFileObject(self,fileid):
        try:
            filejson = self.collection.find_one(ObjectId(fileid))
            if(filejson is not None):
                log.logger.info('file do not exist')
            return filejson
        except KeyError:
            log.logger.error('value of the key does not existed please check the input data')
        except NameError:
            log.logger.error('error of none data')

"""
base operation of the db
"""
class DBBaseOperation:
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
                if(collection not in collectionList):
                    log.logger.warning("collection don't existed and create a new collection")
                self.collection=self.db[collection]
        except:
            log.logger.error("mongo db connection failed!")

    #close connection
    def __del__(self):
        try:
            self.client.close()
            self.client=None
            self.db=None
            self.collection=None
            log.logger.info('disconnect mongoDB')
        except:
            log.logger.error('disconnect mongoDB error')

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

    #find data list in the collection
    #param iJson:search infomation of json format
    def find_list(self,iJson):
        assert self.collection is not None
        return self.collection.find(iJson)

    #list file count 
    #param iJson:search infomation of json format   
    def file_list_count(self,iJson):
        assert self.collection is not None
        return self.collection.find(iJson).count()