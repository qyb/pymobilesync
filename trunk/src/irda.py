from struct import *
from socket import *
import os

def firstHint(hint):
    hint = ord(hint)
    if hint & 0x01:
        print "HINT_PNP"
    if hint & 0x02:
        print "HINT_PDA"
    if hint & 0x04:
        print "HINT_COMPUTER"
    if hint & 0x08:
        print "HINT_PRINTER"
    if hint & 0x10:
        print "HINT_MODEM"
    if hint & 0x20:
        print "HINT_FAX"
    if hint & 0x40:
        print "HINT_LAN"
    if hint & 0x80:
        print "HINT_EXTENSION"

def secondHint(hint):
    hint = ord(hint)
    if hint & 0x01:
        print "HINT_TELEPHONY"
    if hint & 0x02:
        print "HINT_FILE_SERVER"
    if hint & 0x04:
        print "HINT_COMM"
    if hint & 0x08:
        print "HINT_MESSAGE"
    if hint & 0x10:
        print "HINT_HTTP"
    if hint & 0x20:
        print "HINT_OBEX"

class irda:
    def __init__(self):
        self.irda_socket = socket(AF_IRDA, SOCK_STREAM)
        self.timeout = 10

    def discover(self, hints=None):
        self.devicelist = []
        info = self.irda_socket.getsockopt(SOL_IRLMP, IRLMP_ENUMDEVICES, 1024)
        num = unpack('i', info[:4])[0]
        info = info[4:]
        for i in range(num):
            device = []
            if os.name == 'nt':
                deviceinfo = unpack('i22sccc', info[:29])
                info = info[29:]
                device.append(deviceinfo[0])
                device.append(deviceinfo[1].strip('\x00'))
                device.append(deviceinfo[4])
                device.append(deviceinfo[2])
                device.append(deviceinfo[3])
            else:
                deviceinfo = unpack('2i22sccc', info[:33])
                info = info[33:]
                device.append(deviceinfo[1])
                device.append(deviceinfo[2].strip('\x00'))
                device.append(deviceinfo[3])
                device.append(deviceinfo[4])
                device.append(deviceinfo[5])
            self.devicelist.append(device)
        return self.devicelist

    def connect(self, service=None, addr=None):
        if addr == None:
            self.discover(self)
            addr = self.devicelist[0][0]
        if service == None:
            service = 'IrDA:IrCOMM'
        self.irda_socket.connect((addr, service))
        
    def disconnect(self):
        self.irda_socket.close()

    def write(self, data, timeout=10):
        if self.timeout != timeout:
            self.irda_socket.settimeout(timeout)
            self.timeout = timeout
        self.irda_socket.sendall(data)

    def read(self, bufsize=None, timeout=10):
        if self.timeout != timeout:
            self.irda_socket.settimeout(timeout)
            self.timeout = timeout
        return self.irda_socket.recv(bufsize)

if __name__ == '__main__':
    irdaobject = irda()
    devicelist = irdaobject.discover()
    print devicelist
    firstHint(devicelist[0][3])
    secondHint(devicelist[0][4])
    irdaobject.connect('OBEX')
    irdaobject.disconnect()
