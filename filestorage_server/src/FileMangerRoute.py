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
sys.path.append('../')
from flask import Flask, Response, jsonify, make_response, request
from flask_restful import Resource, reqparse
import FileStoreServer.log as log
#upload large file 
#first upload the data in piece and merge the file into one file
#upload the data into the mongoDB GridFS

class LargeFileUploadChunk(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        task = request.form.get('task_id')  # 获取文件的唯一标识符
        chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
        filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

        upload_file = request.files['file']
        upload_file.save('%s/%s' %("./src/data/tmp", filename))  # 保存分片到本地
        return make_response(jsonify({'success': filename+' upload success'}), 200)
    
    def get(self):
        return self.post()

class LargeFileUploadFinished(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        target_filename = request.data["filename"]
        task = request.data["task_id"]              # 获取文件的唯一标识符
        fileInfo = request.data["fileInfo"]
        chunk = 0  # 分片序号
        with open('%s/%s' %("./src/data/tmp", target_filename), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = '%s/%s%s' % ("./src/data/tmp",task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                    chunk += 1
                    os.remove(filename)  # 删除该分片，节约空间
                except IOError:
                    log.logger.error('file chunk does not existed')

        #将文件写入数据库中
        filepath = '%s/%s' %("./src/data/tmp", target_filename)
        fileInfo["upload_path"]=uuid.uuid1()
        
        return make_response(jsonify({'success': target_filename + ' upload success'}),200)
    
    def get(self):
        return self.post()

#upload small data and directly store the binnary data into mongoDB 
class SmallFileUpload(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        return "success"
    
    def get(self):
        return self.post()


class LargeFileDownload(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        return "success"
    
    def get(self):
        return self.post()

class SmallFileDownload(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        return "success"
    
    def get(self):
        return self.post()