import os

from sqlitepb import *

def init_dir(path):
    if os.path.isdir(path) == True:
        return True
    if os.path.exists(path) == True:
        return False
    os.mkdir(path)
    return True

def init():
    if os.path.isdir(os.environ['APPDATA']) == False:
        return False

    data_dir = os.path.join(os.environ['APPDATA'], 'pymobilesync')
    if init_dir(data_dir) == False:
        return False

    sqlite_dir = os.path.join(data_dir, 'sqlite')
    if init_dir(sqlite_dir) == False:
        return False

    mapping_dir = os.path.join(data_dir, 'mapping')
    if init_dir(mapping_dir) == False:
        return False
    mapping_sqlite = os.path.join(mapping_dir, 'sqlite')
    if init_dir(mapping_sqlite) == False:
        return False
    mapping_thunderbird = os.path.join(mapping_dir, 'thunderbird')
    if init_dir(mapping_thunderbird) == False:
        return False

    return True

def s_mapping_dir(filename):
    return os.path.join(os.environ['APPDATA'],
                        'pymobilesync',
                        'mapping',
                        'sqlite',
                        filename)

def sqlite_init(filename):
    file_path = os.path.join(os.environ['APPDATA'],
                            'pymobilesync',
                            'sqlite',
                            filename + '.sqlite')
    if init_dir(s_mapping_dir(filename)) == False:
        return False
    pb = sqlitepb(file_path)
    return pb

if __name__ == '__main__':
    init()
    pb = sqlite_init('local')
    pb.close()
