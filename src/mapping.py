#mapping file format
#First Line: Device Database Name
#Secon Line: Local Modify Time
#Third Line: Remote Anchor
#...
#uid:luid
#...

import time

class mapping:

    def set_file(self, filename):
        self.mapping_file = filename
        return
    
    def __init__(self, filename):
        self.set_file(filename)
        #print self.mapping_file
        return
    
    def parse(self):
        #print self.mapping_file
        try:
            fp = file(self.mapping_file)
            self.did = fp.readline().strip()
            print self.did
            self.timestamp = fp.readline().strip()
            print self.timestamp
            self.anchor = fp.readline().strip()
            print self.anchor
            ret = []
            m = []
            uid = {}
            luid = {}
            for x in fp.readlines():
                y = x.strip().split(':')
                m.append(y)
                uid[y[0]] = y[1]
                luid[y[1]] = y[0]
            fp.close()
            ret.append(m)
            ret.append(uid)
            ret.append(luid)
            return ret
        except:
            return None

    def insert_pair(self, data, uid, luid):
        data[0].append([uid, luid])
        data[1][uid] = luid
        data[2][luid] = uid
        return data

    def remove_pair(self, data, uid, luid):
        error = 1
        for i in range(len(data[0])):
            if data[0][i][0] == uid:
                if data[0][i][1] == luid:
                    error = 0
                    break
        if error == 1:
            return False
        if data[1].has_key(uid) == False:
            return False
        if data[2].has_key(luid) == False:
            return False
        del data[0][i:i+1]
        del data[1][uid]
        del data[2][luid]
        return True

    def set_did(self, did):
        self.did = did
        return

    def set_anchor(self, anchor):
        self.anchor = anchor
        return
    
    def save(self, data):
        #data = [[uid, luid], [uid, luid], [uid, luid], ...]
        fp = file(self.mapping_file, 'w')
        print 'self.did:', self.did
        fp.write(self.did + '\n')
        fp.write(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) + '\n')
        fp.write(self.anchor + '\n')
        for x in data:
            fp.write(x[0] + ':' + x[1] + '\n')
        fp.close()
        return