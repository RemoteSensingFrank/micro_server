#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Frank.Wu'

"""
UNIT TEST for mongoGFS
"""
import unittest
import sys
sys.path.append('../')
import src.mongoGFS as mongoGFS
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

    def testFileAttachInit(self):
        print('init function test')
        fileAttach = mongoGFS.DBFileAttach()
        self.assertNotEqual(None,fileAttach)
 
    #test save file into database success
    def test_AddFileWithObjectSuccess(self):
        print('insert function test')


    #test list find collection in one condition success and failure
    def test_listFileInfoOneCondition(self):
        optDB = mongoGFS.DBBaseOperation()
        filelist1=[]
        filefind = optDB.find_list({"file_department":"GEDI"})
        for item in filefind:
            filelist1.append(item)

        filelist2=[]
        filefind = optDB.find_list({"file_belonged":"wuwei"})
        for item in filefind:
            filelist2.append(item)

        filelist3=[]
        filefind = optDB.find_list({"file_belonged":"test"})
        for item in filefind:
            filelist3.append(item)

        self.assertNotEqual(len(filelist1),0)
        self.assertNotEqual(len(filelist2),0)
        self.assertEqual(len(filelist3),0)

    #test list find collection in muti conditions
    def test_listFileInfoMutiCondition(self):
        optDB = mongoGFS.DBBaseOperation()
        fileInfo1={
            "file_department"   :"GEDI",
            "file_belonged"     :"wuwei",
            "file_descriptor"   :"test upload file"
        }
        filelist1=[]
        filefind = optDB.find_list(fileInfo1)
        for item in filefind:
            filelist1.append(item)

        fileInfo2={
            "file_department"   :"nobody",
            "file_belonged"     :"wuwei",
            "file_descriptor"   :"test upload file"
        }
        filelist2=[]
        filefind = optDB.find_list(fileInfo2)
        for item in filefind:
            filelist2.append(item)

        self.assertNotEqual(len(filelist1),0)
        self.assertEqual(len(filelist2),0)

    #test download Large file
    def test_downloadLargeFile(self):
        filepath='D:\\python\\micro_server\\filestorage_server\\data\\test.zip'
        fileAttach = mongoGFS.DBFileAttach()
        with open(filepath,"ab") as fobj:
            dataGenerator=fileAttach.downloadFileAttach('5c22f47fe991a63eccbd7601')
            for chunk in dataGenerator:
                fobj.write(chunk)
            fobj.close()
        

if __name__ == '__main__':
    unittest.main()#运行所有的测试用例