import json


def load_database_info():
    info = {}
    try:
        db_config = open('../db.info', 'r')
    except IOError:
        print('ERROR: Invalid \'db.info\'...exiting')
        return None

    info['secret_key'] = db_config.readline().strip()
    info['host'] = db_config.readline().strip()
    info['user'] = db_config.readline().strip()
    info['password'] = db_config.readline().strip()
    info['db'] = db_config.readline().strip()
    db_config.close()
    return info


def list_to_string(l):
    return json.dumps(l)


def string_to_list(s):
    return json.loads(s)


def check_unique_user(username, email, mysql):
    cur = mysql.connection.cursor()
    res1 = cur.execute('SELECT * FROM users WHERE username = %s', [username])
    res2 = cur.execute('SELECT * FROM users WHERE email = %s', [email])
    cur.close()
    return res1 > 0 or res2 > 0