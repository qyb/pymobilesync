from pysqlite2 import dbapi2 as sqlite

class sqlitepb:
    def __init__(self, filename):
        if filename == None:
            self.con = sqlite.connect("sqlite.pb")
        else:
            self.con = sqlite.connect(filename)
        self.cur = self.con.cursor()
        self.cur.execute("create table IF NOT EXISTS localpb (  \
                    localpb_id INTEGER PRIMARY KEY,             \
                    m_time TEXT DEFAULT CURRENT_TIMESTAMP,      \
                    surname TEXT,                               \
                    firstname TEXT,                             \
                    email TEXT,                                 \
                    mobile TEXT,                                \
                    home TEXT,                                  \
                    work TEXT,                                  \
                    addr TEXT,                                  \
                    title TEXT,                                 \
                    birthday TEXT,                              \
                    category TEXT,                              \
                    org TEXT                                    \
                    )")

    def fetchall(self):
        self.cur.execute("select * from localpb")
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.con.commit()
        self.con.close()

    def insert(self, data):
        self.cur.execute("insert into localpb (                     \
                         surname, firstname, email, mobile, home,   \
                         work, addr, org, title, birthday, category \
                         ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
        rowid = self.cur.lastrowid;
        return str(rowid)

    def delete(self, rowid):
        self.cur.execute("delete from localpb where localpb_id=" + rowid)
        return True

    def update(self, rowid, cmd):
        self.cur.execute("update localpb set " + cmd + " where localpb_id=" + rowid)
        return True
    
    def execute(self, cmd):
        self.cur.execute(cmd)
        return True

if __name__ == '__main__':
    pb = sqlitepb('004601012106440-449117B5.sqlite')
    print pb.fetchall()
    '''pb = sqlitepb('abc.pb')
    print pb.fetchall(), '\n'
    
    data = ['qyb', 'qyb@eyou.net', '13910177625', '62222324', '58205999',
            'beijing', 'eyou', 'employee', '1977/11/24', 'home']
    rowid = pb.insert(data)
    print rowid, '\n'
    print pb.fetchall(), '\n'

    pb.update(rowid, 'addr = "tianjin"')
    print pb.fetchall(), '\n'
    
    pb.insert(['qyt', 'qyt@eyou.com', '13910177625', '62222324', '58205999',
            'beijing', 'eyou', 'employee', '1977/11/24', 'home'])
    print pb.fetchall(), '\n'
    
    pb.delete(rowid)
    print pb.fetchall(), '\n'
    '''

    pb.close()
