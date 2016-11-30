#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import os

class TomcatFunc(object):
    def __init__(self):
        pass

#关闭tomcat
def killTomcat(tomcatKillScriptPath,tomcatTag=None):
    if not tomcatKillScriptPath:
        FormatPrint.printError("tomcat关闭脚本路径未指定")
        return False
    if  tomcatTag == None:
        FormatPrint.printError("未指定关闭的tomcat")
        return False
    else:
        FormatPrint.printInfo("当前关闭的tomcat编号为"+str(tomcatTag))
        command=str(tomcatKillScriptPath)+" "+str(tomcatTag)
        FormatPrint.printDebug("当前执行的命令为:"+str(command))
        if os.system(command) == 0:
            FormatPrint.printInfo("关闭tomcat" + str(tomcatTag) + "成功")
            return True
        else:
            FormatPrint.printInfo("关闭tomcat"+str(tomcatTag)+"失败")
            return False

#启动tomcat
def startTomcat(tomcatStartScriptPath,tomcatTag=None):
    if not tomcatStartScriptPath:
        FormatPrint.printError("tomcat启动脚本路径未指定")
        return False
    if  tomcatTag == None:
        FormatPrint.printError("未指定启动的tomcat")
        return False
    else:
        FormatPrint.printInfo("当前启动的tomcat编号为"+str(tomcatTag))
        command=str(tomcatStartScriptPath)+" "+str(tomcatTag)
        FormatPrint.printDebug("当前执行的命令为:"+str(command))
        if os.system(command) == 0:
            FormatPrint.printInfo("启动tomcat" + str(tomcatTag) + "成功")
            return True
        else:
            FormatPrint.printInfo("启动tomcat" + str(tomcatTag) + "失败")
            return False

# 重启tomcat
def restartTomcat(tomcatStartScriptPath,tomcatKillScriptPath,tomcatTag=None):
    if killTomcat(tomcatKillScriptPath,tomcatTag) and startTomcat(tomcatStartScriptPath,tomcatTag):
        FormatPrint.printInfo("重启tomcat成功")
        return True
    else:
        FormatPrint.printInfo("重启tomcat失败")
        return False

# 重启tomcat组
def restartTomcats(tomcatStartScriptPath,tomcatKillScriptPath,tomcatTags=None):
    FormatPrint.printInfo("重启tomcat"+str(tomcatTags))
    for tomcatTag in tomcatTags:
        killTomcat(tomcatKillScriptPath, tomcatTag)
        startTomcat(tomcatStartScriptPath, tomcatTag)
    FormatPrint.printInfo("重启tomcat"+str(tomcatTags)+"动作完成")
    return True




