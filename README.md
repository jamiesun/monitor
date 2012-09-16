montior
=======

## config file

> A python script named config

    # -*- coding: utf-8 -*-
    all_config = dict(

        hosts =  [
            ('198.168.8.8',22,u"开发虚拟机"),
            ('198.168.8.1',22,u"")
        ],

        keyfile = '',

        commands = {
            u"磁盘信息" : "df -h",
            u"系统负载" : "uptime",
            u"内存信息" : "free -m",
            u"网卡信息" : "ifconfig",
            u"路由信息" : "route"
        }

    )

    