#!/usr/bin/env python
#coding:utf-8
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import json
import zlib
import time

class Montior():
    def get_cpu_state():
        pass


class EchoClientDatagramProtocol(DatagramProtocol):
    strings = [
        "Hello, world!00000000000000000000000000000000000",
        "What a fine day it is.0000000000000000000000000000000000",
        "Bye-bye!0000000000000000000000000000",
        "Bye-bye!0000000000000000000000000000",
        "Bye-bye!0000000000000000000000000000",
        "Bye-bye!0000000000000000000000000000"
    ]

    def startProtocol(self):
        self.transport.connect('127.0.0.1', 9000)
        self.sendDatagram()
    
    def sendDatagram(self):
        if len(self.strings):
            datagram = self.strings.pop(0)
            self.transport.write(zlib.compress(json.dumps(dict(value=datagram))))
        else:
            reactor.stop()

    def datagramReceived(self, datagram, host):
        print 'Datagram received: ', repr(datagram)
        self.sendDatagram()

    def connectionLost(self, reason):
        print 'lost'

    def connectionRefused(self):
        print 'refund wait 2 second and retry'
        time.sleep(2)
        self.sendDatagram()




def main():
    protocol = EchoClientDatagramProtocol()
    reactor.listenUDP(0, protocol)
    reactor.run()

if __name__ == '__main__':
    main()
