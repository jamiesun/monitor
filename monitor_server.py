#coding:utf-8

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import zlib


# Here's a UDP version of the simplest possible protocol
class EchoUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        print address
        destr =  zlib.decompress(datagram)
        print len(destr),destr
        self.transport.write(datagram, address)

def main():
    reactor.listenUDP(9000, EchoUDP())
    reactor.run()

if __name__ == '__main__':
    main()

