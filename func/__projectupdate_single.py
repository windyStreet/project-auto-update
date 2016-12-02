#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import TomcatFunc
import __checkServiceIsOK
import NodeRunStatusFunc
import ResourceFunc

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
        self.willUpdateGroup="groupmaster"
        self.willBeRestartTomcats=[]
        self.tomcatstartscriptpath = None
        self.tomcatkillscriptpath=None

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
    __pus.willBeRestartTomcats=projectJson.tomcatConf['projectname'][projectJson.projectName]['groupmaster']['tomcatgroupinfo']['tomcats']

    #替换资源
    if ResourceFunc.replceResource(__pus):
        if TomcatFunc.restartWillUpdateTomcatGroup(__pus):
            if len(__checkServiceIsOK.checkServiceIsOk(__pus)) > 0 :
                if NodeRunStatusFunc.modifyNodeHealthStatus(__pus):
                    FormatPrint.printInfo(" update finish ")
                else:
                    FormatPrint.printFalat(" modify ")
            else:
                FormatPrint.printFalat(" service is not available ")
        else:
            FormatPrint.printFalat(" restart tomcat fail ")
    else:
        FormatPrint.printFalat(" replace resource fail ")