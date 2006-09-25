from obex import *

if __name__ == '__main__':
    obexobject = obex()
    obexobject.transport = ObexIrda()
    
    obexobject.transport_connect()
    
    #obexobject.connect('IRMC-SYNC')
    obexobject.connect('')
    if obexobject.handle_connect() == False:
        print 'fetch devinfo error'
        exit

    print 'get devinfo.txt'
    info = obexobject.getfile("telecom/devinfo.txt")
    print info
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

    print 'get pb.vcf...'
    content = obexobject.getfile("telecom/pb.vcf")
    fp = file(unique_code + '.vcf','wb')
    fp.write(content)
    fp.close()
    
    obexobject.disconnect()
    obexobject.handle_input()

    obexobject.transport_disconnect()
