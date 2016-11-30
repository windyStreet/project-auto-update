#!/usr/bin/env python
#!-*- coding:utf-8 -*-

import FormatPrint
import os
class NginxFunc(object):
    def __init__(self):
        pass

#关闭nginx
def killNginx(cmd):
    FormatPrint.printInfo("关闭nginx")
    FormatPrint.printInfo("执行命令:"+str(cmd))
    if os.system(cmd) == 0:
        FormatPrint.printInfo("关闭nginx成功")
        return True
    else:
        FormatPrint.printInfo("关闭nginx失败")
        return False

#启动nginx
def startNginx(cmd):
    FormatPrint.printInfo("启动nginx")
    FormatPrint.printInfo("执行命令:"+str(cmd))
    if os.system(cmd) == 0:
        FormatPrint.printInfo("启动nginx成功")
        return True
    else:
        FormatPrint.printInfo("启动nginx失败")
        return False

#重载nginx
def reloadNginx(cmd):
    FormatPrint.printInfo("重载nginx")
    FormatPrint.printInfo("执行命令:"+str(cmd))
    if os.system(cmd) == 0:
        FormatPrint.printInfo("重载nginx成功")
        return True
    else:
        FormatPrint.printInfo("重载nginx失败")
        return False