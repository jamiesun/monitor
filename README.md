montior
=======

## config file

> A python script named config

    # -*- coding: utf-8 -*-
    all_config = dict(

        hosts =  {
            '192.168.1.8' : {'port':22,'keyfile':'ssh.key','desc':u"开发虚拟机"},
        },


        commands = {
            u"01-操作系统" : 'head -n 1 /etc/issue && uname -a',
            u"02-磁盘信息" : "df -h",
            u"03-系统负载" : "uptime",
            u"04-内存信息" : "free -m",
            u"05-cpu信息" : "grep 'model name' /proc/cpuinfo",
            u"06-网卡信息" : "ifconfig",
            u"07-路由信息" : "route",
            u"08-监听端口" : "netstat -lntp",
            u"09-网络统计信息" : "netstat -s",
            u"10-radusd进程" : "ps aux | grep radiusd",
            u"11-dhcpd进程" : "ps aux | grep dhcpd",
            u"12-所有进程" : "ps aux | sort -k4nr",
        }

    )

    