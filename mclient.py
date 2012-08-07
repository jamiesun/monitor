#!/usr/bin/env python
#coding:utf-8
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import json
import zlib
import time
import os

def pack_data(dtype,dataobj):
    data = dict(authkey="lymonitor",type=dtype,value=dataobj)
    return zlib.compress(json.dumps(data))

def get_uptime():
    cout = os.popen("uptime | awk '{print $3,$8,$9,$10}'" )
    data = [st.strip() for st in cout.read().split(",")]
    return pack_data("uptime",data)

def get_disk_usage():
    disks = []
    cout = os.popen("df -h | awk '$(NF-1)~/\%/ && $NF~/\// {print $NF,$(NF-1)}'" )
    for line in  cout.read().strip().splitlines():
        obj = line.split()
        if len(obj) == 2:
            disks.append(dict(disk=obj[0],usage=obj[1]))
    return pack_data("disk_usage",disks)

def get_memary_usage():
    cout = os.popen("free -m | awk '/buffers\/cache/{print $3,$4}'")
    used,free = (int(uf.strip()) for uf in cout.read().split())
    usage = round(used/((used+free)*1.0)*100,2)
    return pack_data("memary_usage",usage)


class MonitorClientDatagramProtocol(DatagramProtocol):

    def startProtocol(self):
        self.transport.connect('198.168.8.139', 9000)
        self.sendDatagram()
    
    def sendDatagram(self):
        while True:
            time.sleep(5)
            self.transport.write(get_uptime())
            self.transport.write(get_disk_usage())
            self.transport.write(get_memary_usage())


    def datagramReceived(self, datagram, host):
        print 'Datagram received: ', repr(datagram)


    def connectionRefused(self):
        print 'connectionRefused'



def main():
    protocol = MonitorClientDatagramProtocol()
    reactor.listenUDP(0, protocol)
    reactor.run()

if __name__ == '__main__':
    main()
