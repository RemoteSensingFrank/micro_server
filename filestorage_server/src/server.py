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
   http://IP:Port/machinelearning/version_info/resource?params
for Post request：
   http://IP:Port/machinelearning/version_info/action
"""


import src.routes.RecongnizeRoutes as recongize
import instance.app as app
import instance.api as api


#help info 
@app.route('/machinelearning/v1.0.0/help') 
def help(): 
   return 'help info' 

#api.add_resource(recongize.FastrcnnRoute,'/machinelearning/v1.0.0/fastrcnn_recongnize')


# 启动实例 
if __name__ == '__main__': 
   app.run(host='0.0.0.0',port=8081)