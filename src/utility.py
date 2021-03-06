import json
from datetime import datetime


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


def build_mc_data(options):
    results = []
    total_sum = 0
    for num in options.values():
        total_sum += num

    if total_sum == 0:
        for option in options.keys():
            result = {'option': option, 'num': options[option],
                      'percent': "0%"}
            results.append(result)
    else:
        for option in options.keys():
            result = {'option': option, 'num': options[option],
                      'percent': str(round(options[option] / total_sum * 100)) + "%"}
            results.append(result)
    return results


def after_today(t1):
    if t1 is None:
        return False
    t1 = datetime.strptime(t1, '%Y-%m-%dT%H:%M')
    current_time = datetime.now()
    if t1 > current_time:
        return True
    else:
        return False


def load_email_info():
    info = {}
    try:
        email_config = open('../email.info', 'r')
    except IOError:
        print("WARNING: Unable to open 'email.info' file. "
              "Email functionality will be disabled until a valid file is provided.")
        return None

    info['host'] = email_config.readline().strip()
    info['port'] = email_config.readline().strip()
    info['account'] = email_config.readline().strip()
    info['password'] = email_config.readline().strip()
    email_config.close()
    if len(info.keys()) != 4:  # If we haven't parsed everything, or we parsed too much return error
        return None
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


def create_tables(mysql):
    cur = mysql.connection.cursor()
    res = cur.execute("SHOW TABLES LIKE \'companies\'")
    if res < 1:
        print("Creating company table...")
        cur.execute("CREATE TABLE companies(companyID INT(12) PRIMARY KEY AUTO_INCREMENT, companyName VARCHAR(100))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'users\'")
    if res < 1:
        print("Creating user table...")
        cur.execute(
            "CREATE TABLE users(companyID INT(18), ID INT(18) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150), username VARCHAR(30), password VARCHAR(100), positionTitle VARCHAR(100), email VARCHAR(100), startDate VARCHAR(20), FOREIGN KEY (companyID) REFERENCES companies(companyID))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'surveys\'")
    if res < 1:
        print("Creating survey table...")
        cur.execute(
            "CREATE TABLE surveys(managerID INT(18), surveyID INT(18) AUTO_INCREMENT PRIMARY KEY, surveyName VARCHAR(100), surveyCreationDate VARCHAR(20),surveyReleaseDate VARCHAR(20), surveyCompletionDate VARCHAR(20), FOREIGN KEY (managerID) REFERENCES users(ID))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'questions\'")
    if res < 1:
        print("Creating questions table...")
        cur.execute(
            "CREATE TABLE questions(questionID INT(18) AUTO_INCREMENT PRIMARY KEY, surveyID INT(18), questionTitle VARCHAR(500), questionType VARCHAR(50), questionOptions VARCHAR(800), FOREIGN KEY(surveyID) REFERENCES surveys(surveyID))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'emails\'")
    if res < 1:
        print("Creating email table...")
        cur.execute(
            "CREATE TABLE emails(ID INT(18) AUTO_INCREMENT PRIMARY KEY, email VARCHAR(100), surveyID INT(18), FOREIGN KEY (surveyID) REFERENCES surveys(surveyID))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'responses\'")
    if res < 1:
        print("Creating response table...")
        cur.execute(
            "CREATE TABLE responses(responseID INT(18) AUTO_INCREMENT PRIMARY KEY, questionID INT(18), response VARCHAR(500), FOREIGN KEY (questionID) REFERENCES questions(questionID))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'hashes\'")
    if res < 1:
        print("Creating hashes table...")
        cur.execute("CREATE TABLE hashes(hash VARCHAR(50) PRIMARY KEY, surveyID INT(18), used BOOLEAN not null default 0, FOREIGN KEY (surveyID) REFERENCES surveys(surveyID))")
        mysql.connection.commit()
    cur.close()
