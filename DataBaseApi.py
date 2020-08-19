import os
import psycopg2
import datetime

# 連線資料庫
DATABASE_URL = os.environ['DATABASE_URL']

def control_database_with_response(commant):
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur=conn.cursor()
        # 輸入資料庫指令
        cur.execute(commant)
        results=cur.fetchall()
        # 除了Delete之外的指令執行都需要commit()
        conn.commit()
        # 結束連線
        cur.close()
        return results
    except Exception as e:
        print("執行sql時出錯：%s" % (e))
        conn.rollback()
        # 結束連線
        cur.close()
    
def control_database(commant):
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur=conn.cursor()
        # 輸入資料庫指令
        cur.execute(commant)
        # 除了Delete之外的指令執行都需要commit()
        conn.commit()
        # 結束連線
        cur.close()
    except Exception as e:
        print("執行sql時出錯：%s" % (e))
        conn.rollback()
        # 結束連線
        cur.close()

def remove_table(tableName):
    cmdStr = 'DROP TABLE %s;' %tableName
    control_database(cmdStr)

def create_table(tableName, types):
    typeStr = get_full_type_string(types)
    cmdStr = 'CREATE TABLE IF NOT EXISTS %s(%s);' %(tableName, typeStr)
    control_database(cmdStr)
    
def insert_value(tableName, values):
    valueStr = get_full_values_string(values)
    cmdStr = 'INSERT INTO %s VALUES (%s)' %(tableName, valueStr)
    control_database(cmdStr)

def select_table(tableName, keys = '*'):
    keysStr = get_full_keys_string(keys)
    cmdStr = 'SELECT %s FROM %s' %(keysStr, tableName)
    results = control_database_with_response(cmdStr)
    # for r in results:
    #     print(r, type(r))
    return list(results)

def check_value_exists(tableName, keys, selectValue):
    results = select_table(tableName, keys)
    for tup in results:
        if selectValue in tup:
            return True
    return False

def get_full_type_string(types):
    cmdArr = []
    for key, var in types.items():
        cmdArr.append(key + ' ' + var)
    return ', '.join(cmdArr)

def get_full_keys_string(keys):
    if type(keys) == list:
        return ', '.join(keys)
    else:
        return keys

def get_full_values_string(values):
    cmdArr = []
    for var in values:
        if type(var) == str:
            cmdArr.append('\'%s\'' %var)
        elif type(var) == float:
            cmdArr.append('%f' %var)
        elif type(var) == int:
            cmdArr.append('%d' %var)
    return ', '.join(cmdArr)

def get_current_date_str(delta = 0):
    datetime_dt = datetime.datetime.today()
    datetime_str = ''
    # 找時差時間
    if delta != 0:
        deltaDay = datetime.timedelta(days=delta)
        resultDay = datetime_dt + deltaDay
        datetime_str = resultDay.strftime("%Y-%m-%d")
    else:
        datetime_str = datetime_dt.strftime("%Y/%m/%d")
    return datetime_str

def test_database():
    results = control_database_with_response('SELECT VERSION()')
    return "Database version :\n%s " % results

def add_worker_database(user_id):
    tableName = 'workers'
    types = {
        "worker_id": "VARCHAR(50) NOT NULL",
        "deadline": "date"
    }
    create_table(tableName, types)
    if not check_value_exists(tableName, 'worker_id', user_id):
        todayStr = get_current_date_str()
        insert_value(tableName, [user_id, todayStr])
    print(select_table(tableName))

remove_table('workers')