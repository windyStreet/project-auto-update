#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import FormatPrint
import socket
import time
import TomcatFunc
import urllib2
import json

'''
检查tomcat服务是否可用
par:pu
return:sucess service tomcatTags
'''
def checkServiceIsOk(pu):

    projectName = pu.projectName
    willUpdateGroup = pu.willUpdateGroup[0]
    hostinfostr = pu.hostInfostr

    tomcat_conf = pu.projectJson.tomcatConf
    maxTime = tomcat_conf['tomcatmaxrestattime']
    endTime = tomcat_conf['endUpdateWaiteMaxTime']
    tomcatKillScriptPath = tomcat_conf['projectname'][pu.projectName][willUpdateGroup]['tomcatkillscriptpath']
    restartTomcats = tomcat_conf['projectname'][projectName][willUpdateGroup]['tomcatgroupinfo']['tomcats']
    healCheckUrl = tomcat_conf['projectname'][projectName][willUpdateGroup]['servicecheckurl']
    checkData = tomcat_conf['projectname'][projectName][willUpdateGroup]['servicecheckpar']

    socket.setdefaulttimeout(5)
    sucessRestartTomcattags=[]
    tomcatStartTime = time.time()

    restartTomcatTagDict={}
    for tomcatInfo in restartTomcats:
        restartTomcatTagDict[tomcatInfo['tomcattag']]=tomcatInfo

    while True:
        intervalTime = time.time() - tomcatStartTime
        FormatPrint.printInfo("tomcat重启，服务检查耗时:" + str(intervalTime))
        if len(restartTomcatTagDict) == 0 or (intervalTime > float(maxTime) and len(sucessRestartTomcattags) > 0):
            for tomcatTag in sucessRestartTomcattags:
                FormatPrint.printInfo("tomcat" + str(tomcatTag) + "启动成功")
            # 记得关闭未启动成功的tocmat
            if len(restartTomcatTagDict) > 0:
                for failTocmatTag in restartTomcatTagDict:
                    TomcatFunc.killTomcat(tomcatKillScriptPath, failTocmatTag)
            break
        if intervalTime > float(endTime):
            FormatPrint.printFalat("在最大重启时间内，未发现已经完成启动的tomcat，终止更新")
            return sucessRestartTomcattags
        deltomcatTags=[]
        for tomcatTag in restartTomcatTagDict.keys():
            tomcat = restartTomcatTagDict[tomcatTag]
            checkUrl = "http://" + tomcat["serviceip"] + ":" + tomcat["port"] +str(healCheckUrl)
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
                    FormatPrint.printInfo(str(hostinfostr)+"_"+str(projectName)+"项目，tomcat"+str(tomcatTag)+"更新成功")
                    FormatPrint.printInfo("开始更新时间:" + str(tomcatStartTime))
                    FormatPrint.printInfo("更新结束时间:" + time.strftime('%Y-%m-%d %H:%M:%S'))
                    FormatPrint.printInfo("####################################################################")
                    sucessRestartTomcattags.append(tomcatTag)
                    deltomcatTags.append(tomcatTag)
            except Exception as e:
                FormatPrint.printWarn(str(hostinfostr)+"_" + str(projectName) +"tomcat" +str(tomcatTag) + "更新异常:" + str(e))
        if (len(deltomcatTags) > 0):
            for deltag in deltomcatTags:
                del restartTomcatTagDict[deltag]
        time.sleep(3)
        #清空deltomcatTags 临时变量
        del deltomcatTags[:]
    return sucessRestartTomcattags