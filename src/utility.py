def load_database_info():
    info = {}
    try:
        db_config = open('../db.info', 'r')
    except IOError:
        print('ERROR: Create a file called \'db.info\' in the root directory...exiting')
        db_config = open('../db.info', 'w')
        db_config.write('secretkey\n')
        db_config.write('localhost\n')
        db_config.write('root\n')
        db_config.write('password\n')
        db_config.write('database\n')
        db_config.close()
        return None

    info['secret_key'] = db_config.readline().strip()
    info['host'] = db_config.readline().strip()
    info['user'] = db_config.readline().strip()
    info['password'] = db_config.readline().strip()
    info['db'] = db_config.readline().strip()
    db_config.close()
    return info
