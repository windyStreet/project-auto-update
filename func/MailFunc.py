#!/usr/bin/env python
#!-*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import JsonFileFunc
import sys
import os
import FormatPrint

class MailFunc(object):
    def __init__(self):
        self.mailConf = None
        self.message = None
        self.sender = None
        self.receiver = None
    #发送邮件
    def sendMail(self):
        msg = MIMEText("abc", 'plain', 'utf-8')
        msg['From']=formataddr(["管理员",'yaogc@longrise.com.cn'])#显示发件人信息
        msg['To'] = formataddr(["yaogc", 'yaogc@longrise.com.cn'])#显示收件人信息
        msg['Subject'] = "mailFunc Test"  # 定义邮件主题
        try:
            # 创建SMTP对象
            server = smtplib.SMTP("smtp.longrise.com.cn", 25)
            server.set_debuglevel(1)#可以打印出和SMTP服务器交互的所有信息
            # server.set_debuglevel(1)
            # login()方法用来登录SMTP服务器
            server.login("yaogc@longrise.com.cn", "20141021")
            # sendmail()方法就是发邮件，由于可以一次发给多个人，所以传入一个list，邮件正文是一个str，as_string()把MIMEText对象变成str
            server.sendmail('yaogc@longrise.com.cn', ['yaogc@longrise.com.cn', 'zhangcx@longrise.com.cn',], msg.as_string())
            print "邮件发送成功!"
            server.quit()
        except smtplib.SMTPException as e:
            print "Error: 无法发送邮件"+str(e)


    def initMailConf(self):
        mailConfPath = sys.path[0] + os.sep + 'conf' + os.sep + 'tomcat-conf.json'
        self.mailConf = JsonFileFunc.readFile(mailConfPath)
        if self.mailConf is None:
            FormatPrint.printError("tomcat-conf.json file is not exist")

def sendMail(level):
    pass
def initMailCofFile():
    pass


if __name__ == '__main__':
    MF=MailFunc()
    MF.sendMail()
