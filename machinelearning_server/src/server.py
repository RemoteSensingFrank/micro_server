#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Author:Frank.Wu
Date:2018-12-16
version:1.0.0
email:wuwei_cug@163.com
github:https://github.com/RemoteSensingFrank

template of the restful api:
for Post request：
   http://IP:Port/mlserver/version_info/model/detect
"""
import sys
import fastrcnnRoute as fastrcnnRoute
import instance

api = instance.api
app = instance.app

#help info 
@app.route('/mlserver/v1.0.0/help') 
def help(): 
   return 'help info' 

api.add_resource(fastrcnnRoute.FastRCNNDetectRoute,   '/mlserver/v1.0.0.0/fastrcnn/detect')
api.add_resource(fastrcnnRoute.FastRCNNModelRoute,   '/mlserver/v1.0.0.0/fastrcnn/model')



# 启动实例 
if __name__ == '__main__': 
   app.run(host='0.0.0.0',port=8082)