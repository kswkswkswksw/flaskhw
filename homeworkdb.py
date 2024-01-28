import pymysql

db = pymysql.connect(host='localhost', user='root', password='ksw7578609',db='hw1')
cursor = db.cursor()




def create_account(user_name, user_id, user_psw):
    try:
        cursor.execute("select user_no from user_table order by user_no desc limit 1")
        last_no = cursor.fetchone()[0]
    except TypeError:
        last_no = 0
    cursor.execute(f"insert into user_table values ('{user_name}', '{user_id}', '{user_psw}', {last_no+1})")
    cursor.connection.commit()

def list_info():
    cursor.execute("select * from user_table")
    info=cursor.fetchall()
    

    return info


