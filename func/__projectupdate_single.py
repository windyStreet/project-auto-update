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


class __projectupdate_single(object):
    def __init__(self):
        self.projectJson=None
        self.endUpdateWaiteMaxTime=None
        self.tomcatmaxrestattime=None
        self.currentProjectConf=None
        self.projectName = None
        self.updateVersion = None
        self.updateTime = None
        self.updateType = None
        self.deploymentmode = None
        pass

    #初始化node-health-status文件
    def initNodeHealthStatus(self):
        JsonFileFunc.readFile("XX")

def process(projectJson):
    __pus=__projectupdate_single()
    __pus.projectJson=projectJson
    __pus.endUpdateWaiteMaxTime=projectJson['projectname']['endUpdateWaiteMaxTime']
    __pus.tomcatmaxrestattime=projectJson['projectname']['tomcatmaxrestattime']
    __pus.currentProjectConf=__pus.tomcatConf['projectname'][projectJson['projectName']]
    __pus.projectName=projectJson['projectName']
    __pus.updateVersion=projectJson['updateVersion']
    __pus.updateTime=projectJson['updateTime']
    __pus.updateType=projectJson['updateType']
    __pus.deploymentmode=projectJson['deploymentmode']

    __pus.initNodeHealthStatus()

'''
    A、关闭健康检查服务
        B、读取配置文件
        C、初始化node-health-status文件
            1、初始化文件
        D、替换资源
        E、重启tomcat
    F、启动健康检查服务
'''
initNodeHealthStatus()