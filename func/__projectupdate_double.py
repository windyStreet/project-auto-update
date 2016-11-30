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

class __projectupdate_double(object):
    def __init__(self):
        print('__projectupdate_double')

'''
    A、关闭健康检查服务
    B、读取配置文件
    C、初始化tomcatgrup-runstatus文件以及nginxgroup-runstatus文件
        1、判断当前运行组
        2、配置tomcat信息为将运行组tomcat的信息
    D、替换资源
        1、判断当前运行组
        2、替换将被更新组配置的项目
    E、重启tomcat
        1、判断当前运行组
        2、重启将被更新组的tomcat
    F、启动健康检查服务
'''