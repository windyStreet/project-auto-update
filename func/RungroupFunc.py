#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import FormatPrint
import os
import sys
import json

class RunGroup(object):
    def __init__(self):
        pass

    #获取运行组信息(哪一组正在运行)
    def getName(selef,projectName):
        try:
            with open(sys.path[0]+os.sep+'runtime'+os.sep+'nginx-group-runstatus.json') as nginx_group_runstatus_file:
                nginx_group_runstatus_JSON=json.load(nginx_group_runstatus_file)
        except Exception as e:
            FormatPrint.printFalat("获取运行组信息(哪一组正在运行),nginx-group-runstatus.json出现异常:"+str(e));
            exit(-1)
        try:
            with open(sys.path[0] + os.sep + 'runtime' + os.sep + 'tomcat-group-runstatus.json') as tomcat_group_runstatus_file:
                tomcat_group_runstatus_JSON = json.load(tomcat_group_runstatus_file)
        except Exception as e:
            FormatPrint.printFalat("获取运行组信息(哪一组正在运行),tomcat-group-runstatus.json出现异常:" + str(e));
            exit(-1)
        if nginx_group_runstatus_JSON["projectname"][projectName]["currentrun"] == tomcat_group_runstatus_JSON["projectname"][projectName]["currentrun"]:
            return nginx_group_runstatus_JSON["projectname"][projectName]["currentrun"]
        else:
            FormatPrint.printFalat("无法获取"+projectName+"项目运行组的状态")
            sys.exit(-1)

# 重启tomcat
def getRunGroupName(projectName):
    return RunGroup().getName(projectName)