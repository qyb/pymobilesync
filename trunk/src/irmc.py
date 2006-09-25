from obex import *
from sqlitepb import *
from vcf import *
from mapping import *
import util
import os
import time

def fillVCF(x, key):
    if x.has_key(key) == False:
        x[key] = ''

def fillVcard(i):
    fillVCF(i, 'email')
    fillVCF(i, 'CELL')
    fillVCF(i, 'HOME')
    fillVCF(i, 'WORK')
    fillVCF(i, 'org')
    fillVCF(i, 'title')
    fillVCF(i, 'birthday')
    fillVCF(i, 'category')

def genVcardName(surname, firstname, charset):
    ret = 'N;CHARSET='+charset+':'
    ret += surname.encode(charset)
    ret += ';'
    ret += firstname.encode(charset)
    return ret

def genVcardEmail(email):
    return 'EMAIL;INTERNET:' + email

def genVcardHome(home):
    return 'TEL;HOME:' + home

def genVcardWork(work):
    return 'TEL;WORK:' + work

def genVcardCell(mobile):
    return 'TEL;CELL:' + mobile

def genVcardOrg(org, charset):
    return 'ORG;CHARSET='+charset+':' + org.encode(charset)

def genVcardTitle(title, charset):
    return 'TITLE;CHARSET='+charset+':' + title.encode(charset)

def genVcardBirthday(birthday):
    return 'BDAY:' + birthday

def genVcardCategory(category, charset):
    return 'X-ESI-CATEGORIES;CHARSET='+charset+':' + category.encode(charset)

def genVCARD(i):
    '''localpd_id m_time surname firstname email
    mobile home work addr org
    title birthday category'''
    ret = 'BEGIN:VCARD\r\nVERSION:2.1\r\n'
    ret += genVcardName(i[2], i[3], 'UTF-7') + '\r\n'
    ret += genVcardEmail(i[4]) + '\r\n'
    ret += genVcardCell(i[5]) + '\r\n'
    ret += genVcardHome(i[6]) + '\r\n'
    ret += genVcardWork(i[7]) + '\r\n'
    ret += genVcardOrg(i[9], 'UTF-7') + '\r\n'
    ret += genVcardTitle(i[10], 'UTF-7') + '\r\n'
    ret += genVcardBirthday(i[11]) + '\r\n'
    ret += genVcardCategory(i[12], 'UTF-7') + '\r\n'
    ret += 'END:VCARD\r\n'
    return str(ret)
    
def sync(remoteData, localData, obexobject, mobject, map_info):
    print remoteData
    print localData
    pb = util.sqlite_init('local')
    for i in remoteData[0]:
        x = pb.insert([i['name'][0],
                       i['name'][1],
                       i['email'],
                       i['CELL'],
                       i['HOME'],
                       i['WORK'],
                       '',
                       i['org'],
                       i['title'],
                       i['birthday'],
                       i['category']
                       ])
        print 'add pb:', x
        mobject.insert_pair(map_info, str(x), i['luid'])
    for i in remoteData[1]:
        uid = int(map_info[2][i['luid']])
        update_string = ''
        update_string = pb.updateSQL(update_string, 'firstname', i['name'][1])
        update_string = pb.updateSQL(update_string, 'surname', i['name'][0])
        if i.has_key('HOME'):
            update_string = pb.updateSQL(update_string, 'home', i['HOME'])
        if i.has_key('CELL'):
            update_string = pb.updateSQL(update_string, 'mobile', i['CELL'])
        if i.has_key('WORK'):
            update_string = pb.updateSQL(update_string, 'work', i['WORK'])
        if i.has_key('org'):
            update_string = pb.updateSQL(update_string, 'org', i['org'])
        if i.has_key('title'):
            update_string = pb.updateSQL(update_string, 'title', i['title'])
        if i.has_key('birthday'):
            update_string = pb.updateSQL(update_string, 'birthday', i['birthday'])
        if i.has_key('category'):
            update_string = pb.updateSQL(update_string, 'category', i['category'])
        pb.update(uid, update_string)
        print 'update pb:', uid
    for luid in remoteData[2]:
        uid = map_info[2][luid]
        pb.delete(int(uid))
        print 'delete pb:', uid
        mobject.remove_pair(map_info, uid, luid)
    pb.close()

    current_anchor = obexobject.getfile("telecom/pb/luid/cc.log").strip()
    mobject.set_anchor(current_anchor)
    
    for i in localData[0]:
        uid = str(i[0])
        vcard = genVCARD(i)
        ret = obexobject.putfile("telecom/pb/luid/.vcf", vcard)
        print ret
        luid = ret[0][2]
        mobject.set_anchor(ret[1][2])
        mobject.insert_pair(map_info, uid, luid)
        print mobject.anchor
        
    for i in localData[1]:
        uid = str(i[0])
        vcard = genVCARD(i)
        luid = map_info[1][uid]
        ret = obexobject.putfile("telecom/pb/luid/" + luid + ".vcf", vcard)
        print ret
        luid = ret[0][2]
        mobject.set_anchor(ret[1][2])
        print mobject.anchor

    for uid in localData[2]:
        luid = map_info[1][uid]
        mobject.remove_pair(map_info, uid, luid)
        ret = obexobject.delfile("telecom/pb/luid/" + luid + ".vcf")
        print 'delete device:', luid, ret
        mobject.set_anchor(ret[1][2])
    
    mobject.save(map_info[0])
    return

def slow_sync(obexobject, mobject):
    #current_anchor = obexobject.getfile("telecom/pb/luid/cc.log").strip()
    #mobject.set_anchor(current_anchor)
    vcardlist = parseVCF(obexobject.getfile("telecom/pb.vcf"))
    for i in vcardlist:
        fillVcard(i)
    #analyze local pb
    sync([vcardlist, [], []], [[], [], []], obexobject, mobject, [[], {}, {}])

def fast_sync(obexobject, mobject, mdata, cclog):
    #print mdata
    #print cclog
    
    pb = util.sqlite_init('local')
    addrlist = pb.fetchall()
    pb.close()
    
    pbuid = {}
    for i in addrlist:
        pbuid[str(i[0])] = i[1]

    remote_amd = [[],[],[]]
    for i in cclog:
        if i == '*':
            #change  log full, with hard delete support
            print 'oops, not support CLFwithHD'
            return
        x = i.split(':')
        if len(x) == 3:
            #change  log full, with hard delete support
            #assert x[0] == 'H'
            remote_amd[2].append(x[2])
        else:
            luid = x[3]
            if x[0] == 'M':
                if mdata[2].has_key(luid):
                    #exist in mapping
                    uid = mdata[2][luid]
                    if pbuid.has_key(uid):
                        #exist in pb
                        remote_amd[1].append(luid)
                    else:
                        #exist in mapping, but not in pb
                        #means remove it from pb and modify it on device. THEN SAVE AGAIN!!!
                        remote_amd[0].append(luid)
                        mobject.remove_pair(mdata, uid, luid)
                else:
                    #not exist in mapping
                    remote_amd[0].append(luid)
            else:
                #test for removing from device but modifing on pb
                if mdata[2].has_key(luid):
                    #exist in mapping
                    uid = mdata[2][luid]
                    if pbuid[uid] > mobject.timestamp:
                        #modified! remote it from mapping
                        #then entry will insert into device again
                        mobject.remove_pair(mdata, uid, luid)
                    else:
                        remote_amd[2].append(x[3])
                else:
                    #oops! anyway, add it into remove list 
                    remote_amd[2].append(x[3])

    local_amd = [[], [], []]
    for i in addrlist:
        #print i[1]
        if i[1] > mobject.timestamp:
            #add or modify
            uid = str(i[0])
            if mdata[1].has_key(uid):
                local_amd[1].append(uid)
            else:
                local_amd[0].append(uid)
    for i in mdata[0]:
        uid = i[0]
        if pbuid.has_key(uid) == False:
            #exist in mapping , not in pb
            local_amd[2].append(uid)
    
    remoteData=[[],[],remote_amd[2]]
    for luid in remote_amd[0]:
        vcf = obexobject.getfile("telecom/pb/luid/" + luid + ".vcf")
        vcf = parseVCARD(vcf)
        fillVcard(vcf)
        remoteData[0].append(vcf)
    for luid in remote_amd[1]:
        vcf = obexobject.getfile("telecom/pb/luid/" + luid + ".vcf")
        vcf = parseVCARD(vcf)
        fillVcard(vcf)
        remoteData[1].append(vcf)
    #print remoteData

    localData = [[], [], local_amd[2]]
    pb = util.sqlite_init('local')
    for uid in local_amd[0]:
        localData[0].append(pb.fetchrow(int(uid))[0])
    for uid in local_amd[1]:
        localData[1].append(pb.fetchrow(int(uid))[0])
    #print localData

    sync(remoteData, localData, obexobject, mobject, mdata)
    return

if __name__ == '__main__':
    obexobject = obex()
    obexobject.transport = ObexIrda()
    obexobject.transport_connect()
    obexobject.connect('IRMC-SYNC')
    if obexobject.handle_connect() == False:
        print 'obex IRMC-SYNC error'
        exit

    print 'get devinfo'
    info = obexobject.getfile("telecom/devinfo.txt").split('\r\n')
    dinfo = {}
    for line in info:
        line = line.strip()
        if len(line) == 0:
            break
        kv = line.split(':')
        dinfo[kv[0].strip()] = kv[1].strip()
    unique_code = dinfo['MANU'] + '-' + dinfo['MOD'] + '-' + dinfo['SN']
    print unique_code

    infolog = {}
    for line in obexobject.getfile("telecom/pb/info.log").split():
        kv = line.split(':')
        try:
            infolog[kv[0]] = kv[1]
        except:
            pass
    #print 'DID:', infolog['DID']
    #print 'IEL:', infolog['IEL']
    #print 'SAT:', infolog['SAT']
    #print 'HD:', infolog['HD']
    print infolog

    mapping_file = os.path.join(util.s_mapping_dir('local'), unique_code)
    #print mapping_file

    mobject = mapping(mapping_file)
    mdata = mobject.parse()
    #print mdata
    if mdata == None:
        #slow sync

        mobject.set_did(infolog['DID'])
        slow_sync(obexobject, mobject)
    else:
        cclog = obexobject.getfile("telecom/pb/luid/" + mobject.anchor + ".log")
        print cclog
        cclog = cclog.split('\r\n')
        remoteDID = cclog[1].split(':')[1].split()
        if remoteDID != mobject.did or (len(cclog) > 4 and cclog[4] == '*'):
            mobject.set_did(remoteDID)
            slow_sync(obexobject, mobject)
        else:
            del cclog[0:4]
            print 'fastsync...,'
            fast_sync(obexobject, mobject, mdata, cclog)
    
    obexobject.disconnect()
    obexobject.handle_input()
    obexobject.transport_disconnect()
