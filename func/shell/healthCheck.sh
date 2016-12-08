#!/bin/bash

if [ -n "$2" ] ; then
    projectname=$2
    echo $projectname
else
    echo "no specify project name "
    exit 1
fi

workspace=$(cd $(dirname $0)/; pwd)
cd $workspace
cd ../
curDIR=`pwd`
ControlerFile=$curDIR/Controler.py
healthchecklog=$workspace/nohuplogs/$projectname-healthcheck.log
pidfile=$curDIR/run/$projectname-healthcheak.pid
pidfiledir=$curDIR/run

function check_pid() {
    if [ -f $pidfile ];then
        pid=`cat $pidfile`
        if [ -n $pid ]; then
            running=`ps -p $pid|grep -v "PID TTY" |wc -l`
            return $running
        fi
    fi
    return 0
}

#启动健康检查
function start()
{
    if [ ! -d $pidfiledir ] ; then
	mkdir -p $pidfiledir
    fi
    check_pid
    running=$?
    if [ $running -gt 0 ];then
        echo -n "healthcheck  now is running already, pid="
        cat $pidfile
	return 1
    fi
    nohup python $ControlerFile -m healthCheckAll -P $projectname > $healthchecklog 2>&1 &
    sleep 1
    running=`ps -p $! | grep -v "PID TTY" | wc -l`
    if [ $running -gt 0 ];then
        echo $! > $pidfile
	echo `date +"%Y-%m-%d %H:%M:%S"`启动healthcheck服务...... >> $healthchecklog
        echo "healthcheck started..., pid=$!"
    else
	echo "healthcheck failde to start."
	return 1
    fi
}

#关闭健康检查
function stop()
{
    if [ -f  $pidfile ] ; then
        pid=`cat $pidfile`
        kill $pid
        rm -rf $pidfile
	echo `date +"%Y-%m-%d %H:%M:%S"`关闭healthcheck服务......  >> $healthchecklog
	echo "healthcheck stoped..."
    else
        echo "pid file not exist"
    fi
}

#重启健康检查
function restart()
{
    stop
    sleep 1
    start
}

#健康检查运行状态
function status()
{
    check_pid
    running=$?
    if [ $running -gt 0 ];then
        echo started
    else
        echo stoped
    fi
}


if [ -n "$1" ] ; then
    if [ "$1" ==  "start" ] ; then
       start
    elif [ "$1" == "stop" ] ; then
       stop
    elif [ "$1" == "restart" ] ; then
       restart
    elif [ "$1" == "status" ] ; then
       status
    else
        echo "only support start|stop|restart|status"
   fi
else
    echo "need par start|stop|restart|status"
fi
