#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
protocol: 
desc:Using to upload and down load the file using file storage
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
from flask import Flask, Response, jsonify, make_response, request,send_file
from flask_restful import Resource, reqparse
import mimetypes
parser = reqparse.RequestParser()
parser.add_argument('filepath', type=str, location='args')
parser.add_argument('filename', type=str, location='args')

#server
import log as log
import fileStorage as fStorage
import instance as instance

configure   = instance.conf

#upload large file 
#first upload the data in piece and merge the file into one file
class LargeFileUploadChunk(Resource):
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


#merge all the chunk and restore the file into file system storage
class LargeFileUploadFinished(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        chunk           = 0  # 分片序号
        upload_dir      = request.data["dstdir"]
        task            = request.data["task_id"]     
        target_filename = request.data["filename"]
        fileInfo        = request.data["fileInfo"]
        fileOptEx = fStorage.FileIOEx()
        dstdir = '%s/%s' %("../data", upload_dir)
        #it will take some time to merge the file
        with fileOptEx.open('%s/%s' %(upload_dir, target_filename), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = '%s/%s%s' % (dstdir,task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                    chunk += 1
                    os.remove(filename)  # 删除该分片，节约空间
                except:
                    log.logger.error('upload merge file failed')
                    target_file.close()
                    fileOptEx.remove('%s/%s' %(upload_dir, target_filename))
                    err=configure.get("return_info","file_upload_error")
                    return make_response(jsonify({'error': 'upload the file failed'}),err)
        return make_response(jsonify({'success': target_filename + ' upload success'}),200)

    def get(self):
        return self.post()

#upload small data save the file into file system
class SmallFileUploadMongo(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        file        = request.files.get('file')
        upload_dir  = request.data["dstdir"]
        fileInfo    = request.data["fileInfo"]
        filename    = fileInfo['filename']
        fileOptEx   = fStorage.FileIOEx()
        fileOptEx.save(file,'%s/%s' %(upload_dir,filename))
        return make_response(jsonify({'success upload success'}),200)
    
    def get(self):
        return self.post()

#file down load using send_file
#do not need to consider the size of the file
#send_file function considered the chunk
class FileDownload(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        args = parser.parse_args()
        filepath = args.get('filepath')
        filename = args.get('filename')

        fileOptEx   = fStorage.FileIOEx()
        fobj = fileOptEx.open('%s/%s' %(filepath,filename),'rb')
        mime_type = mimetypes.guess_type(filename)[0]
        if(mime_type==None):
            mime_type = 'application/octet-stream'
        response = make_response(send_file(fobj,mimetype=mime_type,as_attachment=True,attachment_filename=filename))
        response.headers["Content-Length"]=fileOptEx.size('%s/%s' %(filepath,filename))
        return response

    def get(self):
        return self.post()