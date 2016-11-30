#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import time
# 格式化info输出
def printInfo(object):
    print("[INFO]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object))
# 格式化error输出
def printError(object):
    print("[ERROR]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object))
# 格式化warn输出
def printWarn(object):
    print("[WARR]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object))
# 格式化debug输出
def printDebug(object):
    print("[DEBUG]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object))
#格式化fatal输出
def printFalat(object):
    print("[FALAT]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object))