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

class __projectupdate_onehalf(object):
    def __init__(self):
        print('__projectupdate_onehalf')
'''
    A、关闭健康检查服务
    B、读取配置文件
    C、初始化tomcatgrup-runstatus文件以及nginxgroup-runstatus文件
        i:single模式需要初始化全部的tomcat信息，master以及backup两组的tomcat信息
    D、替换资源
    E、重启tomcat
        1:修改nginx文件（剔除mastert 服务配置）
        2:reload nginx
        3:重启master tomcat
        4:修改nginx文件（剔除backup  ，添加master 服务配置）
        5:reload nginx
        6:重启backup tomcat
        7:修改nginx文件（添加master以及backup服务配置）
        8:reload nginx
     F、启动健康检查服务
'''