#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import sys
import os
import json
import time
import urllib2
import socket
import FormatPrint
import TomcatFunc
import NginxFunc

class __projectupdate_single(object):
    def __init__(self):
        print('__projectupdate_single')

'''
    A、关闭健康检查服务
        B、读取配置文件
        C、初始化tomcatgroup-runstatus文件以及nginxgroup-runstatus文件
        D、替换资源
        E、重启tomcat
    F、启动健康检查服务
'''