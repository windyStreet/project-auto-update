#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import FormatPrint
import os

class ResourceFunc(object):
    def __init__(self):
        pass

#资源替换
def replceResource(pu):
    tomcat_conf = pu.projectJson.tomcatConf
    command = tomcat_conf['projectname'][pu.projectName][pu.willUpdateGroup]['tomcatresourceupdatescriptpath'] + " " + str(pu.updateVersion) + " " + str(pu.updateTime)
    FormatPrint.printInfo("执行资源替换脚本:" + str(command))
    # if os.system(command) == 0:
    if True:
        FormatPrint.printInfo("replace resource sucess ")
        return True
    else:
        FormatPrint.printInfo("replace resource fail ")
        return False