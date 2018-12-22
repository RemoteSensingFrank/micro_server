#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Frank.Wu'

"""
UNIT TEST for mongoGFS
"""
import unittest
import sys
sys.path.append('../')
import FileStoreServer.control.mongoGFS as mongoGFS
import FileStoreServer.instance as instance

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


    def testFileAttachInit(self):
        print('init function test')
        fileAttach = mongoGFS.DBFileAttach()
        self.assertNotEqual(None,fileAttach)


    def test_AddFileWithAttachSuccess(self):
        print('insert function test')
        fileInfo={
            "file_department"   :"GEDI",
            "file_belonged"     :"wuwei",
            "file_attach_path"  :"D:\\python\\machine_server_with_mongo\\src\\src\\data\\test\\test.zip",
            "file_descriptor"   :"test upload file"
        }
        fileAttach = mongoGFS.DBFileAttach()
        self.assertEqual(fileAttach.insertFileAttach(fileInfo),configure.get("return_info","success")) 

        
if __name__ == '__main__':
    unittest.main()#运行所有的测试用例