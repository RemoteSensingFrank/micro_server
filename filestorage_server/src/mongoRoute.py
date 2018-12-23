#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
protocol: 
desc:Using to upload and down load the file
compiler:python3.6.x
created by  : Frank.Wu
company     : GEDI
created time: 2018.12.16
version     : version 1.0.0.0
"""

import json
import sys
import os
import uuid

#flask
from flask import Flask, Response, jsonify, make_response, request
from flask_restful import Resource, reqparse

#server
import log as log
import mongoGFS as mongoGFS
import instance as instance

configure   = instance.conf
#upload large file 
#first upload the data in piece and merge the file into one file
#then upload the data into the mongoDB GridFS
class LargeFileUploadChunkMongo(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        #first get the file and store the file locally 
        task = request.form.get('task_id')      # 获取文件的唯一标识符
        chunk = request.form.get('chunk', 0)    # 获取该分片在所有分片中的序号
        upload_dir  = request.form.get('dstdir')# 目标文件夹路径以便于进行区分
        
        filename = '%s%s' % (task, chunk)       # 构造该分片的唯一标识符
        upload_file = request.files['file']
        dstdir = '%s/%s' %("../data", upload_dir)

        if not os.path.isdir(dstdir):
            os.makedirs(dstdir)
        upload_file.save('%s/%s' %(dstdir, filename))  # 保存分片到本地
        return make_response(jsonify({'success': filename+' upload success'}), 200)
    
    def get(self):
        return self.post()

class LargeFileUploadFinishedMongo(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        chunk           = 0  # 分片序号
        dstdir          = request.data["dstdir"]
        task            = request.data["task_id"]     
        target_filename = request.data["filename"]
        fileInfo        = request.data["fileInfo"]

        #it will take some time to merge the file
        with open('%s/%s' %(dstdir, target_filename), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = '%s/%s%s' % (dstdir,task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                    chunk += 1
                    os.remove(filename)  # 删除该分片，节约空间
                except IOError:
                    log.logger.error('file chunk does not existed')

        #write the file into mongoDB
        filepath = '%s/%s' %(dstdir, target_filename)
        fileInfo["upload_path"]     =uuid.uuid1()
        fileInfo["file_attach_path"]=filepath

        mongoAttach = mongoGFS.DBFileAttach()
        rs=mongoAttach.insertFileAttach(fileInfo)
        if(rs!=configure.get("return_info","success")):
            return make_response(jsonify({'error': 'upload the file failed'}),rs)
        else:
            return make_response(jsonify({'success': target_filename + ' upload success'}),200)
    
    def get(self):
        return self.post()

#upload small data and directly store the binnary data into mongoDB 
class SmallFileUploadMongo(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        file        = request.files.get('file')
        dstdir      = request.data["dstdir"]
        fileInfo    = request.data["fileInfo"]
        filepath = '%s/%s' %(dstdir, file.filename)
        fileInfo["file_attach_path"]  = filepath
        fileObjOpt=mongoGFS.DBFileObject()
        fileObjOpt.insertFileAttach(file,fileInfo)
        
        return "success"
    
    def get(self):
        return self.post()

class LargeFileDownloadMongo(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        return "success"
    
    def get(self):
        return self.post()

class SmallFileDownloadMongo(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        return "success"
    
    def get(self):
        return self.post()