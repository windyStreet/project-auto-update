#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import sys
import os
import FormatPrint
import socket
import time
import TomcatFunc
import urllib2
import json
import JsonFileFunc

# 检查服务是否可用
# 检查tomcat服务是否可用
def checkServiceIsOk(restartTomcats,projectName,maxTime,endTime,tomcatKillScriptPath,hostinfostr):
    socket.setdefaulttimeout(5)
    nodeHealthStatusFile = sys.path[0] + os.sep + 'runtime' + os.sep + str(projectName) +'-node-health-status.json'
    nodeHealthStatus= JsonFileFunc.readFile(nodeHealthStatusFile)

    sucessRestartTomcats=[]
    tomcatStartTime = time.time()
    while True:
        intervalTime = time.time() - tomcatStartTime
        FormatPrint.printInfo("tomcat重启，服务检查耗时:" + str(intervalTime))
        if len(restartTomcats) == 0 or (intervalTime > float(maxTime) and len(sucessRestartTomcats) > 0):
            for tomcatTag in sucessRestartTomcats:
                FormatPrint.printInfo("tomcat" + str(tomcatTag) + "启动成功")
            # 记得关闭未启动成功的tocmat
            if len(restartTomcats) > 0:
                for failTocmatTag in restartTomcats:
                    TomcatFunc.killTomcat(tomcatKillScriptPath, failTocmatTag)
            break
        if intervalTime > float(endTime):
            FormatPrint.printFalat("在最大重启时间内，未发现已经完成启动的tomcat，终止更新")
            return sucessRestartTomcats
        delList=[]
        for tomcatTag in restartTomcats:
            checkUrl=nodeHealthStatus[tomcatTag]['health-check-url']
            checkData=nodeHealthStatus[tomcatTag]['health-check-data']
            try:
                response = urllib2.urlopen(checkUrl, checkData)
                ret_data = response.read()
                ret_code = response.code

                response.close()
                if isinstance(ret_data, bytes):
                    ret_data = bytes.decode(ret_data)
                ret_data = json.loads(ret_data)
                if ret_data["status"] == 1 and ret_code == 200:
                    FormatPrint.printInfo("####################################################################")
                    FormatPrint.printInfo("tomcat更新记录如下:")
                    FormatPrint.printInfo(hostinfostr+"_"+str(projectName)+"项目，tomcat"+tomcatTag+"更新成功")
                    FormatPrint.printInfo("开始更新时间:" + str(tomcatStartTime))
                    FormatPrint.printInfo("更新结束时间:" + time.strftime('%Y-%m-%d %H:%M:%S'))
                    FormatPrint.printInfo("####################################################################")
                    # 更新成功，将tomcat的标识加入到delList中
                    delList.append(tomcatTag)
                    sucessRestartTomcats.append(tomcatTag)
            except Exception as e:
                FormatPrint.printWarn(hostinfostr+"_" + str(projectName) +"tomcat" +tomcatTag + "更新异常:" + str(e))
        if (len(delList) > 0):
            # 删除delList中的tomcat标识，这些tomcat已经更新完成
            for deltag in delList:
                del restartTomcats[deltag]
        time.sleep(3)
        # delList.clear()
        del delList[:]
    return sucessRestartTomcats