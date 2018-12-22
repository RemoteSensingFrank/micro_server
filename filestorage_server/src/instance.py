import sys
from flask import Flask 
from flask_restful import Api
import configparser


#instance in the program
app = Flask(__name__)
api = Api(app)
conf=configparser.ConfigParser()
conf.read('src/config.conf')

