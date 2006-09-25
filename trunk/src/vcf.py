import quopri

def decodeString(vstring, setting):
    if setting.has_key('ENCODING'):
        if setting['ENCODING'] == "QUOTED-PRINTABLE":
            vstring = quopri.decodestring(vstring)
    if setting.has_key('CHARSET'):
        vstring = vstring.decode(setting['CHARSET'])
    return vstring

'''def parseVstring(vstring, prop):
    charset = ''
    encoding = ''
    #print vstring
    #print prop
    for i in prop:
        if i[:9] == "ENCODING=":
            encoding = i[9:]
            break
    if encoding == "QUOTED-PRINTABLE":
        vstring = quopri.decodestring(vstring)

    #print vstring
    
    for i in prop:
        if i[:8] == "CHARSET=":
            charset = i[8:]
    #print charset
    if charset != '':
        vstring = vstring.decode(charset)
    return vstring


#CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:G=E5=85=B3=E4=BA=8C=E5=B8=85;\
#   CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:G=E5=85=B3=E4=BA=8C=E5=B8=85
def _parseString(vstring):
    xret = []
    s = 0
    meet = 0
    prop = []
    for i in range(len(vstring)):
        if vstring[i] == ';':
            if meet == 0:
                prop.append(vstring[s:i])
            else:
                meet = 0
                ret = parseVstring(vstring[s:i], prop)
                xret.append(ret)
                prop = []
            s = i+1
        if vstring[i] == ':':
            prop.append(vstring[s:i])
            s = i+1
            meet = 1
    ret = parseVstring(vstring[s:], prop)
    xret.append(ret)
    return xret

def parseString(vstring):
    ret = _parseString(vstring)
    return ret[0]

def printVCARD(vcard):
    for i in vcard:
        if i == 'name':
            if len(vcard[i]) == 1:
                print 'name:', vcard[i][0]
            else:
                print 'name:', vcard[i][0], vcard[i][1]
        else:
            print '%s:'%i, vcard[i]

def getSetting(s):
    ret = {}
    x = s.split(';')
    for y in x:
        z = y.split('=')
        if len(z) == 2:
            ret[z[0]] = z[1]
    return ret
'''
def parseVCARD(src):
    vcard = {}
    #vcard['tel'] = []
    #vcard['email'] = []
    lines = src.splitlines()
    #print lines
    for line in lines:
        line = line.split(':')
        keylist = line[0].split(';')
        setting = {}
        for x in keylist:
            y = x.split('=')
            if len(y) == 2:
                setting[y[0]] = y[1]
        key = keylist[0]
        valuelist = line[1].split(';')
        value = valuelist[0]
        
        if key == "BEGIN" or key == "END" or key == "VERSION":
            continue
        if key == "N":
            vcard['name'] = [u'', u'']
            vcard['name'][0] = decodeString(valuelist[0], setting)
            if len(valuelist) == 2:
                vcard['name'][1] = decodeString(valuelist[1], setting)
        elif key == "TEL":
            vcard[keylist[1]] = value
        elif key == "ORG":
            vcard['org'] = decodeString(value, setting)
        elif key == "EMAIL":
            vcard['email'] = value
        elif key == "X-IRMC-LUID":
            vcard['luid'] = value
        elif key == "X-ESI-CATEGORIES":
            vcard['category'] = decodeString(value, setting)
        elif key == "BDAY":
            vcard['birthday'] = value
        elif key == "TITLE":
            vcard['title'] = decodeString(value, setting)
        else:
            print line
            pass
        '''if line == "BEGIN:VCARD" or line == "END:VCARD" or line[:8] == "VERSION:":
            continue
        if line[0] == "N":
            x = line.split(':')
            name = x[1].split(';')
            setting = getSetting(x[0])
            vcard['name'] = [u'', u'']
            vcard['name'][0] = decodeString(name[0], setting)
            if len(name) == 2:
                vcard['name'][1] = decodeString(name[1], setting)
        elif line[:4] == "TEL;":
            #tel = line[4:]
            #vcard['tel'].append(tel)
            tel = line[4:].split(':')
            vcard[tel[0]] = tel[1]
        elif line[:3] == "ORG":
            x = line.split(':')
            setting = getSetting(x[0])
            vcard['org'] = decodeString(x[1], setting)
        #elif line[:4] == "ORG;":
        #    org = line[4:]
        #    vcard['org'] = parseString(org)
        #elif line[:4] == "ORG:":
        #    vcard['org'] = line[4:]
        elif line[:14] == "EMAIL;INTERNET":
            ### 'EMAIL;INTERNET;PREF:' or 'EMAIL;INTERNET:'
            email = line[14:]
            x = email.find(':')
            #vcard['email'].append(email[x+1:])
            vcard['email'] = email[x+1:]
        elif line[:12] == "X-IRMC-LUID:":
            vcard['luid'] = line[12:]
        elif line[:17] == "X-ESI-CATEGORIES;":
            category = line[17:]
            vcard['category'] = parseString(category)
        elif line[:5] == "BDAY:":
            vcard['birthday'] = line[5:]
        elif line[:5] == "TITLE":
            vcard['title'] = parseString(line[6:])
        else:
            print line
            pass'''

    #printVCARD(vcard); print ""
    return vcard

def parseVCF(src):
    vcardlist = []
    lines = src.splitlines()
    #print lines
    for line in lines:
        #print line
        if line == "BEGIN:VCARD":
            chunk = line + '\r\n'
        elif line[0] == '=':
            # line-wrap for quoted-printable
            chunk = chunk[:-3] + line + '\r\n'
        else:
            chunk += line + '\r\n'
        if line == "END:VCARD":
            vcardlist.append(parseVCARD(chunk))
    return vcardlist
            
if __name__ == "__main__":
    #vfile = "qyb_b.vcf"
    vfile = "qyt.vcf"
    #vfile = "C:\\vcf\\Whole Phonebook.vcf"
    x = file(vfile)
    y = parseVCF(x.read())

    for i in y:
        print '--------------------'
        for j in i:
            if j == 'name':
                print j, i[j][0], i[j][1]
            else:
                print j, i[j]
    #print y
    x.close()
