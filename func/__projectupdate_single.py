#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import sys
import os
import JsonFileFunc
import json
import time
import urllib2
import socket
import FormatPrint
import TomcatFunc
import NginxFunc
import __checkServiceIsOK

class __projectupdate_single(object):
    def __init__(self):
        self.hostInfostr=None
        self.projectJson=None
        self.endUpdateWaiteMaxTime=None
        self.tomcatmaxrestattime=None
        self.currentProjectConf=None
        self.projectName = None
        self.updateVersion = None
        self.updateTime = None
        self.updateType = None
        self.deploymentmode = None
        self.nodeHealthStatus=None
        self.willUpdateGroup="groupmaster"
        self.willBeRestartTomcats=[]
        self.tomcatstartscriptpath = None
        self.tomcatkillscriptpath=None
    pass

    #创建node-health-status文件数据
    def createNodeHealthStatus(self):
        node_health_status = {}
        #通过读取配置文件，将配置文件中的信息初始化到node-health-status文件中
        node_health_status['currentrun']='groupmaster'
        node_health_status['deploymentmode']='single'

        for tomcat in self.currentProjectConf[self.willUpdateGroup]['tomcatgroupinfo']['tomcats']:
            node_name = tomcat['tomcattag']
            health_check_url = "http://" + tomcat["serviceip"] + ":" + tomcat["port"] +self.currentProjectConf[self.willUpdateGroup]['servicecheckurl']
            health_check_data = self.currentProjectConf[self.willUpdateGroup]['servicecheckpar']
            node_health_status[node_name] = {
                'health-check-url':health_check_url,
                'health-check-data':health_check_data,
                'status': 'n/a',
                'last-response-data': 'n/a',
                'last-response-time': 0,
                'fail-count': 0,
                'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.willBeRestartTomcats.append(node_name)
        return node_health_status


    #初始化node-health-status文件
    def initNodeHealthStatus(self):
        node_health_status_file = sys.path[0] + os.sep + 'runtime' + os.sep + str(self.projectName) +'-node-health-status.json'
        self.nodeHealthStatus=JsonFileFunc.readFile(node_health_status_file)
        if self.nodeHealthStatus == None:
            data=self.createNodeHealthStatus()
            self.nodeHealthStatus=data
            JsonFileFunc.createFile(node_health_status_file,data)

    #项目资源替换
    def replceResource(self):
        command = self.currentProjectConf[self.willUpdateGroup]['tomcatresourceupdatescriptpath']+ " " + str(self.updateVersion) + " " + str(self.updateTime)
        FormatPrint.printInfo("执行资源替换脚本:" + str(command))
        if os.system(command) == 0:
            FormatPrint.printInfo("replace resource sucess ")
            return True
        else:
            FormatPrint.printInfo("replace resource fail ")
            return False

    #重启当前tomcat
    def restartCurrentTomcats(self):
        if len(self.willBeRestartTomcats) == 0:
            FormatPrint.printError(" no tomcat is able to restart ")
            return False
        else:
            self.tomcatstartscriptpath = self.currentProjectConf[self.willUpdateGroup]['tomcatstartscriptpath']
            self.tomcatkillscriptpath = self.currentProjectConf[self.willUpdateGroup]['tomcatkillscriptpath']
            return TomcatFunc.restartTomcats(self.tomcatstartscriptpath,self.tomcatkillscriptpath,self.willBeRestartTomcats)


'''
    A、关闭健康检查服务
        B、读取配置文件
        C、初始化node-health-status文件
            1、初始化文件
        D、替换资源
        E、重启tomcat
    F、启动健康检查服务
'''
def process(projectJson):
    __pus=__projectupdate_single()

    __pus.projectJson=projectJson
    __pus.endUpdateWaiteMaxTime=projectJson.tomcatConf['endUpdateWaiteMaxTime']
    __pus.tomcatmaxrestattime=projectJson.tomcatConf['tomcatmaxrestattime']
    __pus.currentProjectConf=projectJson.tomcatConf['projectname'][projectJson.projectName]
    __pus.hostInfostr =projectJson.hostInfostr
    __pus.projectName=projectJson.projectName
    __pus.updateVersion=projectJson.updateVersion
    __pus.updateTime=projectJson.updateTime
    __pus.updateType=projectJson.updateType
    __pus.deploymentmode=projectJson.deploymentmode

    #初始化运行时文件
    __pus.initNodeHealthStatus()
    #替换资源
    if __pus.replceResource():
        if __pus.restartCurrentTomcats():
            if __checkServiceIsOK.checkServiceIsOk(__pus.willBeRestartTomcats,__pus.projectName,__pus.tomcatmaxrestattime,__pus.endUpdateWaiteMaxTime, __pus.tomcatkillscriptpath,__pus.hostInfostr):
                FormatPrint.printInfo(" update finish ")
            else:
                FormatPrint.printFalat(" service is not available ")
        else:
            FormatPrint.printFalat(" restart tomcat fail ")
    else:
        format(" replace resource fail ")


