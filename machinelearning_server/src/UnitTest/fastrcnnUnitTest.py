#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Frank.Wu'

"""
UNIT TEST for mongoGFS
"""
import unittest
import sys
import os
sys.path.append('../')
import src.fastrcnnDetect as fastrcnn
import src.instance as instance

configure   = instance.conf

class MongoGFSTest(unittest.TestCase):  # 继承unittest.TestCase
    def tearDown(self):
        # running after run test case 
        print('finish Test case~')

    def setUp(self):
        # running before test case
        print('start Test case~')

    @classmethod
    def tearDownClass(self):
         print('Finshed all Test case~')

    @classmethod
    def setUpClass(self):
        print('Start Unit Test')

    def testDetecIniVisImage(self):
        dectector = fastrcnn.FastRCNNDetector("D:\\python\\micro_server\\machinelearning_server\model\\fastrcnn\\frozen_inference_graph.pb","D:\\python\\micro_server\\machinelearning_server\model\\fastrcnn\\labelmap.pbtxt")
        rs=dectector.target_detect_visiual_output("D:\\python\\micro_server\\machinelearning_server\\data\\DJI_0005.JPG",0.9)
        self.assertNotEqual(None,rs)


    def testDetecVisImage(self):
        dectector = fastrcnn.FastRCNNDetector()
        rs=dectector.target_detect_visiual_output("D:\\python\\micro_server\\machinelearning_server\\data\\DJI_0005.JPG",0.9)
        self.assertNotEqual(None,rs)

    def testDetectVisBinnary(self):
        dectector = fastrcnn.FastRCNNDetector()
        size = os.path.getsize("D:\\python\\micro_server\\machinelearning_server\\data\\DJI_0005.JPG")
        with open("D:\\python\\micro_server\\machinelearning_server\\data\\DJI_0005.JPG",'rb') as fobj:
            imgBuf = fobj.read(size)
            fobj.close()
            rs=dectector.target_detect_visiual_binnary(imgBuf,0.9)
            self.assertNotEqual(None,rs)

if __name__ == '__main__':
    unittest.main()#运行所有的测试用例