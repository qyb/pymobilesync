import os
import sys

from obex import *
from sqlitepb import *
from vcf import *

def read_anchor(filename):
    anchor = file(filename)
    
    
def write_anchor(filename):
    pass

if __name__ == '__main__':
    obexobject = obex()
    obexobject.transport = ObexIrda()

    obexobject.transport_connect()

    obexobject.connect('IRMC-SYNC')
    ret = obexobject.handle_input()
    if ret == False:
        print 'connect IRMC-SYNC error'
        exit

    #obexobject.getfile("telecom/devinfo.txt")
    #print obexobject.handle_getfile()

    '''obexobject.getfile("telecom/pb.vcf")
    print obexobject.handle_getfile()'''

    #obexobject.getfile("telecom/pb/info.log")
    #print obexobject.handle_getfile()

    obexobject.getfile("telecom/pb/luid/cc.log")
    data = obexobject.parse_file(obexobject.handle_getfile())
    change_counter = data.strip()

    obexobject.getfile("telecom/pb/luid/" + change_counter + ".log")
    data = obexobject.parse_file(obexobject.handle_getfile())
    cclog = data.split()

    SN = cclog[0].split(':')[1]
    DID = cclog[1].split(':')[1]
    mapping_file = SN + '-' + DID + '.mapping'
    sqlite_file = SN + '-' + DID + '.sqlite'
    print mapping_file, sqlite_file
    try:
        x = file(mapping_file)
        anchor = x.readline().strip()
        timestamp = x.readline().strip()
        mapping = x.read().split()
        for i in range(len(mapping)):
            mapping[i] = mapping[i].split(':')
        x.close()
        slow_sync = 0
        print mapping
        print 'slow sync..?'
    except:
        print 'PRINT ERROR:', sys.exc_info()
        slow_sync = 1

    if slow_sync == 0:
        obexobject.getfile("telecom/pb/luid/" + anchor + ".log")
        data = obexobject.parse_file(obexobject.handle_getfile())
        clog = data.split()
        print clog
        clog[:4] = []
        if len(clog) > 0:
            if clog[0] == '*':
                slow_sync = 1

    print 'step1...'
    if slow_sync == 1:
        mappinginfo = ''
        if False:
            obexobject.getfile("telecom/pb.vcf")
            data = obexobject.parse_file(obexobject.handle_getfile())
        else:
            vfile = file("C:\\vcf\\qyb_b.vcf")
            data = vfile.read()
            vfile.close()
        try:
            vcardlist = parseVCF(data)
            if True:
                try:
                    os.remove(sqlite_file)
                except:
                    pass
            pb = sqlitepb(sqlite_file)
            for vcard in vcardlist:
                luid = vcard['luid']
                insertdata = []
                name = vcard.get('name', ['',''])
                insertdata.append(name[0])
                insertdata.append(name[1])
                insertdata.append(vcard.get('email', ''))
                insertdata.append(vcard.get('CELL', ''))
                insertdata.append(vcard.get('HOME', ''))
                insertdata.append(vcard.get('WORK', ''))
                insertdata.append('')
                insertdata.append(vcard.get('org', ''))
                insertdata.append(vcard.get('title', ''))
                insertdata.append(vcard.get('birthday', ''))
                insertdata.append(vcard.get('category', ''))
                rowid = pb.insert(insertdata)
                mappinginfo += luid + ':' + rowid + '\r\n'
            pb.close()
            f = file(mapping_file, "wb")
            f.write(change_counter + '\r\n')
            f.write(datetime.now().ctime() + '\r\n')
            f.write(mappinginfo)
            f.close()
        except:
            print sys.exc_info()
            pass

    else:
        for centry in clog:
            centry = centry.split(':')
            device_luid = centry[3]
            obexobject.getfile("telecom/pb/luid/" + device_luid + ".vcf")
            data = obexobject.parse_file(obexobject.handle_getfile())
            print centry, data

    obexobject.disNclose()
