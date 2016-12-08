#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import time
import sys
import os
# 格式化info输出
def printInfo(object):
    log = "[ INFO]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object)
    writeLogFile(log,"info")
    print(log)
# 格式化error输出
def printError(object):
    log = "[ERROR]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object)
    writeLogFile(log, "err")
    print(log)
# 格式化warn输出
def printWarn(object):
    log = "[ WARN]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object)
    writeLogFile(log, "war")
    print(log)
# 格式化debug输出
def printDebug(object):
    log =  "[DEBUG]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object)
    writeLogFile(log, "debug")
    print(log)
#格式化fatal输出
def printFalat(object):
    log = "[FALAT]" + time.strftime('%Y-%m-%d %H:%M:%S') + "  " + str(object)
    writeLogFile(log, "falat")
    print(log)
    exit(-1)
#日志文件写入
def writeLogFile(logStr,type):
    logPath =  sys.path[0] + os.sep + 'logs' + os.sep + 'log.log'
    if type == 'info':
        typeLogPath = sys.path[0] + os.sep + 'logs' + os.sep + 'info.log'
    elif type == 'err':
        typeLogPath = sys.path[0] + os.sep + 'logs' + os.sep + 'error.log'
    elif type == 'war':
        typeLogPath = sys.path[0] + os.sep + 'logs' + os.sep + 'warning.log'
    elif type == 'debug':
        typeLogPath = sys.path[0] + os.sep + 'logs' + os.sep + 'debug.log'
    elif type == 'falat':
        typeLogPath = sys.path[0] + os.sep + 'logs' + os.sep + 'falat.log'
    else:
        typeLogPath = sys.path[0] + os.sep + 'logs' + os.sep + 'log.log'

    # typeLogFile = open(typeLogPath, 'a')
    # typeLogFile.write(logStr)
    # typeLogFile.close()

    with open(typeLogPath, 'a+') as type_log_file:
        type_log_file.write(logStr+'\n')
    with open(logPath, 'a+') as log_file:
        log_file.write(logStr+'\n')