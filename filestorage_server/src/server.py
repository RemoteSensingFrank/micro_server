#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Author:Frank.Wu
Date:2018-12-16
version:1.0.0
email:wuwei_cug@163.com
github:https://github.com/RemoteSensingFrank

template of the restful api:
for Get request:
   http://IP:Port/filestorage/version_info/storage/resource?params
for Post request：
   http://IP:Port/filestorage/version_info/storage/action
"""
import sys
import mongoRoute as MongoRoute
import instance

api = instance.api
app = instance.app

#help info 
@app.route('/filestorage/v1.0.0/help') 
def help(): 
   return 'help info' 

api.add_resource(MongoRoute.LargeFileUploadChunkMongo,   '/filestorage/v1.0.0.0/mongodb/uploadlargechunk')
api.add_resource(MongoRoute.LargeFileUploadFinishedMongo,'/filestorage/v1.0.0.0/mongodb/uploadlargefinished')
api.add_resource(MongoRoute.SmallFileUploadMongo,        '/filestorage/v1.0.0.0/mongodb/uploadsmall')

api.add_resource(MongoRoute.LargeFileDownloadMongo,      '/filestorage/v1.0.0.0/mongo/downloadlarge')
api.add_resource(MongoRoute.SmallFileDownloadMongo,      '/filestorage/v1.0.0.0/mongo/downloadsmall')
api.add_resource(MongoRoute.SmallFileDownloadAsFileMongo,'/filestorage/v1.0.0.0/mongo/downloadsmallasfile')


# 启动实例 
if __name__ == '__main__': 
   app.run(host='0.0.0.0',port=8081)