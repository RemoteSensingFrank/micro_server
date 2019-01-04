#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
protocol: 
desc:Using upload the picture and return result
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
#flask
from flask import Flask, Response, jsonify, make_response, request,send_file
from flask_restful import Resource, reqparse
import mimetypes

#server
import src.log as log
import src.fastrcnnDetect as fastrcnn
import src.instance as instance

configure   = instance.conf

#run fastrcnn model and return the result
class FastRCNNDetectRoute(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        file   = request.files.get('file')
        imgBuf = file.read()
        dectector = fastrcnn.FastRCNNDetector()
        detect = dectector.target_detect_visiual_binnary(imgBuf,0.9)
        if(detect==None):
            log.logger.error("detected failed")
            return make_response(jsonify({"detected failed"}), configure.get("return_info","detect_failed"))
        else:
            log.logger.info("detected success")
            return make_response(jsonify(detect), 200)
    def get(self):
        return self.post()

#return the data of the model
class FastRCNNModelRoute(Resource):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self):
        mime_type = 'application/octet-stream'
        response = make_response(send_file(fobj,mimetype=mime_type))
        response.headers["Content-Length"]=os.path.size('../moddel/fastrcnn/frozen_inference_graph.pb')
        return response
        
    def get(self):
        return self.post()