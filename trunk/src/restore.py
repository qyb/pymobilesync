from obex import *

if __name__ == '__main__':
    obexobject = obex()
    obexobject.transport = ObexIrda()
    
    obexobject.transport_connect()
    
    obexobject.connect('IRMC-SYNC')
    #obexobject.connect('')
    if obexobject.handle_connect() == False:
        print 'fetch devinfo error'
        exit

    print 'get devinfo.txt'
    info = obexobject.getfile("telecom/devinfo.txt")
    info = info.split('\r\n')
    dinfo = {}
    for line in info:
        line = line.strip()
        if len(line) == 0:
            break
        print 'line:',line
        kv = line.split(':')
        dinfo[kv[0].strip()] = kv[1].strip()
    unique_code = dinfo['MANU'] + '-' + dinfo['MOD'] + '-' + dinfo['SN']
    print unique_code
    
    print 'get info.log'
    print obexobject.getfile("telecom/pb/info.log")

    print 'put pb.vcf...'
    data = file(unique_code + '.vcf','rb').read()
    while True:
        offset = data.find('BEGIN:VCARD', 1)
        if offset == -1:
            ret = obexobject.putfile("telecom/pb/luid/.vcf", data)
            print ret
            break
        else:
            vcf = data[:offset]
            data = data[offset:]
            ret = obexobject.putfile("telecom/pb/luid/.vcf", vcf)
            print ret
    
    obexobject.disconnect()
    obexobject.handle_input()

    obexobject.transport_disconnect()
