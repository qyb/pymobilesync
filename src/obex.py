from irda import *
from datetime import *

OBEX_CMD_CONNECT    = 0x00
OBEX_CMD_DISCONNECT = 0x01
OBEX_CMD_PUT        = 0x02
OBEX_CMD_GET        = 0x03
OBEX_CMD_SETPATH    = 0x05
OBEX_CMD_SESSION    = 0x07
OBEX_CMD_ABORT      = 0x7f
OBEX_FINAL          = 0x80
OBEX_ONECMD_CONNECT     = 0x80
OBEX_ONECMD_DISCONNECT  = 0x81
OBEX_ONECMD_PUT         = 0x82
OBEX_ONECMD_GET         = 0x83
OBEX_ONECMD_SETPATH     = 0x85
OBEX_ONECMD_ABORT       = 0xff

class ObexTrans:

    def listen(self):
        return False

    def disconnect(self):
        return False


class ObexIrda(irda, ObexTrans):

    def connect(self, addr=None):
        irda.connect(self, 'OBEX', addr)

    def handle_input(self):
        return False


class obex:

    transport = ObexTrans()

    def __init__(self):
        self.mtu = 1024
        self.version = 0x10

    def genheader_byte_stream(self, opcode, byte_stream):
        length = htons(3 + len(byte_stream))
        return chr(opcode) + pack('h', length) + byte_stream

    def genheader_unicode(self, opcode, unistr):
        unistr = unistr + '\x00\x00'
        length = htons(3 + len(unistr))
        return chr(opcode) + pack('h', length) + unistr

    def genheader_byte(self, opcode, byte):
        return chr(opcode) + chr(byte)

    def genheader_u32int(self, opcode, data):
        return chr(opcode) + pack('i', htonl(data))

    def genheader(self, opcode, data):
        hi = opcode & 0xc0
        if hi == 0x00:
            return self.genheader_unicode(opcode, data)
        elif hi == 0x40:
            return self.genheader_byte_stream(opcode, data)
        elif hi == 0x80:
            return self.genheader_byte(opcode, data)
        else:
            return self.genheader_u32int(opcode, data)

    def transport_connect(self, addr=None):
        self.transport.connect(addr)
        
    def transport_disconnect(self):
        self.transport.disconnect()

    def connect(self, target):
        header = ''
        if (len(target)):
            header = self.genheader(0x46, target)
        length = htons(7 + len(header))
        cmd = chr(OBEX_ONECMD_CONNECT) + pack('h', length)
        cmd += chr(self.version) + chr(0) + pack('h', htons(self.mtu))
        cmd += header
        return self.transport.write(cmd)

    def disconnect(self):
        cmd = chr(OBEX_ONECMD_DISCONNECT) + pack('h', htons(3))
        return self.transport.write(cmd)

    def getufile(self, filename):
        header = self.genheader(0x01, filename)
        length = htons(3 + len(header))
        cmd = chr(OBEX_ONECMD_GET) + pack('h', length) + header
        return self.transport.write(cmd)

    def getfile(self, filename):
        return self.getufile(filename.encode('utf-16be'))

    def _parse_header(self, data):
        header = []
        opcode = ord(data[0])
        header.append(opcode)
        hi = opcode & 0xc0
        if hi == 0x00 or hi == 0x40:
            length = ntohs(unpack('h', data[1:3])[0])
            header.append(length)
            header.append(data[3:length])
        elif hi == 0x80:
            header.append(2)
            header.append(data[1])
        else:
            header.append(5)
            header.append(ntohl(unpack('i', data[1:5])[0]))
        return header

    def parse_header(self, data):
        headers = []
        while True:
            header = self._parse_header(data)
            headers.append(header)
            next = len(data) - header[1]
            if next == 0:
                return headers
            elif next < 0:
                print 'parse_header error...'
                return headers
            data = data[header[1]:]

    def parse_packet(self, data):
        packet = []
        packet.append(ord(data[0]))
        length = ntohs(unpack('h', data[1:3])[0])
        packet.append(length)
        packet.append(data[3:length])
        return packet

    def handle_input(self, timeout=10):
        end = datetime.now() + timedelta(seconds=timeout)
        data = ''
        while True:
            delta = end - datetime.now()
            if delta.seconds <= 0:
                return False
            data += self.transport.read(delta.seconds)
            if len(data) < 3:
                continue
            packet = self.parse_packet(data)
            if packet[1] == len(data):
                return packet
            elif packet[1] < len(data):
                return False

    def disNclose(self):
        self.disconnect()
        self.handle_input()
        self.transport_disconnect()

    def handle_getfile(self):
        data = self.handle_input()
        headers = self.parse_header(data[2])
        while data[0] == 0x90:
            print 'continue...'
            self.transport.write(chr(OBEX_ONECMD_GET) + pack('h', htons(3)))
            data = self.handle_input()
            headers += self.parse_header(data[2])
        return headers

    def parse_file(self, headers):
        ret = ''
        for header in headers:
            if header[0] == 0x48:
                ret += header[2]
            elif header[0] == 0x49:
                ret += header[2]
                break
        return ret
            
if __name__ == '__main__':
    obexobject = obex()
    obexobject.transport = ObexIrda()

    obexobject.transport_connect()

    obexobject.connect('IRMC-SYNC')
    ret = obexobject.handle_input()

    obexobject.getfile("telecom/devinfo.txt")
    
    #ret = obexobject.handle_input()
    #print obexobject.parse_header(ret[2])
    ret = obexobject.handle_getfile()
    print obexobject.parse_file(ret)
    

    obexobject.disconnect()
    ret = obexobject.handle_input()
    print ret

    obexobject.transport_disconnect()
