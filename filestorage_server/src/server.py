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
import consul

api = instance.api
app = instance.app
conf= instance.conf
#help info 
@app.route('/filestorage/v1.0.0/help') 
def help(): 
   return 'help info' 

#for health check
@app.route('/filestorage/v1.0.0/check', methods=['GET'])  
def check():
   return 'success'

api.add_resource(MongoRoute.LargeFileUploadChunkMongo,   '/filestorage/v1.0.0.0/mongodb/uploadlargechunk')
api.add_resource(MongoRoute.LargeFileUploadFinishedMongo,'/filestorage/v1.0.0.0/mongodb/uploadlargefinished')
api.add_resource(MongoRoute.SmallFileUploadMongo,        '/filestorage/v1.0.0.0/mongodb/uploadsmall')

api.add_resource(MongoRoute.LargeFileDownloadMongo,      '/filestorage/v1.0.0.0/mongo/downloadlarge')
api.add_resource(MongoRoute.SmallFileDownloadMongo,      '/filestorage/v1.0.0.0/mongo/downloadsmall')
api.add_resource(MongoRoute.SmallFileDownloadAsFileMongo,'/filestorage/v1.0.0.0/mongo/downloadsmallasfile')


#services register
def consul_service_register():
   client = consul.Consul()
   service_id = "datastorage-localhost:8081"
   httpcheck  = "http://192.168.1.25:8081/filestorage/v1.0.0/check"
   check = consul.Check.http(httpcheck, "30s")
   client.agent.service.register(name="datastorage",service_id=service_id,address='192.168.1.25',
                  port=8081,tags=['filestorage'],check=check)

#services unregister
def consul_service_unregister():
   client = consul.Consul()
   service_id = "datastorage-localhost:8081"
   client.agent.service.deregister(name="datastorage",service_id=service_id)

# start instance 
if __name__ == '__main__': 
   try:
      consul_service_register()
      app.run(host='0.0.0.0',port=8081)
   except RuntimeError as msg:
      if str(msg) == "Server going down":
         consul_service_unregister();
         print(msg)
      else:
         print("server stopped by accident!")