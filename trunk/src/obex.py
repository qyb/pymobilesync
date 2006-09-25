from irda import *
from datetime import *
from socket import *

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

class ObexIrda(irda, ObexTrans):

    def connect(self, addr=None):
        irda.connect(self, 'OBEX', addr)

    def disconnect(self):
        irda.close(self)
        
    def handle_input(self):
        return False


class obex:

    transport = ObexTrans()

    def __init__(self):
        self.mtu = 1024
        self.version = 0x10

    def genheader_byte_stream(self, opcode, byte_stream):
        length = htons(3 + len(byte_stream))
        return chr(opcode) + pack('H', length) + byte_stream

    def genheader_unicode(self, opcode, unistr):
        unistr = unistr + '\x00\x00'
        length = htons(3 + len(unistr))
        return chr(opcode) + pack('H', length) + unistr

    def genheader_byte(self, opcode, byte):
        return chr(opcode) + chr(byte)

    def genheader_u32int(self, opcode, data):
        return chr(opcode) + pack('I', htonl(data))

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
        cmd = chr(OBEX_ONECMD_CONNECT) + pack('H', length)
        cmd += chr(self.version) + chr(0) + pack('H', htons(self.mtu))
        cmd += header
        return self.transport.write(cmd)

    def disconnect(self):
        cmd = chr(OBEX_ONECMD_DISCONNECT) + pack('H', htons(3))
        return self.transport.write(cmd)

    def _parse_parameter(self, para):
        parameter = []
        parameter.append(ord(para[0]))
        length = ord(para[1]) + 2
        parameter.append(length)
        parameter.append(para[2:length])
        return parameter
        
    def parse_parameter(self, para):
        #print para
        parameters = []
        while True:
            if len(para) < 2:
                return parameters
            parameter = self._parse_parameter(para)
            parameters.append(parameter)
            next = len(para) - parameter[1]
            if next == 0:
                return parameters
            elif next < 0:
                return 'parse_parameter error...'
                return parameters
            para = para[parameter[1]:]
            #print para

    def getufilecmd(self, filename):
        header = self.genheader(0x01, filename)
        length = htons(3 + len(header))
        cmd = chr(OBEX_ONECMD_GET) + pack('H', length) + header
        return self.transport.write(cmd)

    def getfilecmd(self, filename):
        return self.getufilecmd(filename.encode('utf-16be'))

    def putufile(self, filename, data):
        print data
        print len(data)
        chunk_size = 1000
        name_header = self.genheader(0x01, filename)
        length_header = self.genheader(0xc3, len(data))
        first_packet = 1
        while len(data) > chunk_size:
            chunk_data = data[:chunk_size]
            body_header = self.genheader(0x48, chunk_data)
            data = data[chunk_size:]
            if first_packet == 1:
                first_packet = 0
                length = htons(3 + len(name_header) + len(length_header) + len(body_header))
                cmd = chr(OBEX_CMD_PUT) + pack('H', length) + name_header + length_header + body_header
            else:
                length = htons(3 + len(body_header))
                cmd = chr(OBEX_CMD_PUT) + pack('H', length) + body_header
            self.transport.write(cmd)
            ret = self.handle_input()
            if ret[0] == 0x90:
                print 'continue...'
            else:
                print 'oops.', ret

        body_header = self.genheader(0x49, data)
        if first_packet == 1:
            length = htons(3 + len(name_header) + len(length_header) + len(body_header))
            cmd = chr(OBEX_ONECMD_PUT) + pack('H', length) + name_header + length_header + body_header
        else:
            length = htons(3 + len(body_header))
            cmd = chr(OBEX_CMD_PUT) + pack('H', length) + body_header
        self.transport.write(cmd)
        ret = self.handle_input()
        
        if ret[0] != 0xa0:
            print 'oops.', ret
            return False
        headers = self.parse_header(ret[2])
        for header in headers:
            if header[0] == 0x4c:
                #app parameters
                paras = self.parse_parameter(header[2])
                return paras
        return True
        
    def putfile(self, filename, data):
        return self.putufile(filename.encode('utf-16be'), data)

    def delufilecmd(self, filename):
        name_header = self.genheader(0x01, filename)
        #length_header = self.genheader(0xc3, 0)
        #length = htons(3 + len(name_header) + len(length_header))
        length = htons(3 + len(name_header))
        #print ntohs(length)
        #print len(name_header)
        cmd = chr(OBEX_ONECMD_PUT) + pack('H', length) + name_header# + length_header
        self.transport.write(cmd)
        
    def delfilecmd(self, filename):
        return self.delufilecmd(filename.encode('utf-16be'))
    
    def _parse_header(self, data):
        header = []
        opcode = ord(data[0])
        header.append(opcode)
        hi = opcode & 0xc0
        if hi == 0x00 or hi == 0x40:
            length = ntohs(unpack('H', data[1:3])[0])
            header.append(length)
            header.append(data[3:length])
        elif hi == 0x80:
            header.append(2)
            header.append(data[1])
        else:
            header.append(5)
            header.append(ntohl(unpack('I', data[1:5])[0]))
        return header

    def parse_header(self, data):
        headers = []
        while True:
            if len(data) < 2:
                return headers
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
        length = ntohs(unpack('H', data[1:3])[0])
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
            #print data
            packet = self.parse_packet(data)
            if packet[1] == len(data):
                return packet
            elif packet[1] < len(data):
                #print data
                return False

    def disNclose(self):
        self.disconnect()
        self.handle_input()
        self.transport_disconnect()

    def handle_getfilecmd(self):
        data = self.handle_input()
        headers = self.parse_header(data[2])
        while data[0] == 0x90:
            print 'continue...'
            self.transport.write(chr(OBEX_ONECMD_GET) + pack('H', htons(3)))
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

    def getfile(self, filename):
        self.getfilecmd(filename)
        ret = self.handle_getfilecmd()
        return self.parse_file(ret)

    def delfile(self, filename):
        self.delfilecmd(filename)
        ret = self.handle_input()
        if ret[0] != 0xa0:
            print 'oops. delfile error...', ret
            return False
        headers = self.parse_header(ret[2])
        for header in headers:
            if header[0] == 0x4c:
                #app parameters
                paras = self.parse_parameter(header[2])
                return paras
        return True
    
    def handle_connect(self):
        ret = self.handle_input()
        if ret == False:
            self.disconnect()
            self.handle_input()
            self.transport_disconnect()
            return False
        return True
            
if __name__ == '__main__':
    obexobject = obex()
    obexobject.transport = ObexIrda()
    
    obexobject.transport_connect()
    
    obexobject.connect('IRMC-SYNC')
    #obexobject.connect('')
    if obexobject.handle_connect() == False:
        print 'fetch devinfo error'
        exit

    print 'get info.log'
    print obexobject.getfile("telecom/pb/info.log")
    obexobject.disconnect()
    obexobject.handle_input()

    obexobject.connect('IRMC-SYNC')
    if obexobject.handle_connect() == False:
        print 'obex IRMC-SYNC error'
        exit

    print 'emulate removing file'
    ret = obexobject.delfile("telecom/pb/999.log")
    print ret
    
    obexobject.disconnect()
    obexobject.handle_input()

    obexobject.transport_disconnect()
