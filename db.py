import pymysql

db= pymysql.connect(host='localhost',user='root',password='ksw7578609',db='bbs')
cursor = db.cursor()

def login_check(id, password):
    cursor.execute(f"select * from user where id='{id}' and password='{password}'")
    info = cursor.fetchall()
    if info:
        return info[0]
    return info

def join_account(id, password, username):
    try:
        cursor.execute("select user_no from user order by user_no desc limit 1")
        last_no = cursor.fetchone()[0]
    except TypeError:
        last_no = 0
    cursor.execute(f"insert into user values ('{id}', '{password}', '{username}', {last_no+1})")
    cursor.connection.commit()

def bbs_info(contents_id=None):
    if contents_id == None:
        cursor.execute("select * from board") # db가 많다면 where 구문으로 끊어서 처리
    else:
        cursor.execute(f"select * from board where contents_id={contents_id}")
    return cursor.fetchall()

def try_view_amount(contents_id):
    cursor.execute(f"select views from board where contents_id={contents_id}")
    view_amount = cursor.fetchone()[0]
    cursor.execute(f"update board set views={view_amount+1} where contents_id={contents_id}")
    cursor.connection.commit()
    
def write_up_at_db(json, username, user_no):
    try:
        cursor.execute("select contents_id from board order by contents_id desc limit 1")
        last_contents_id = cursor.fetchone()[0]
    except TypeError:
        last_contents_id = 0
    title = json['title']; contents = json['contents']
    cursor.execute(f"""insert into board values ("{username}", {user_no}, "{title}", "{contents}", 1, {last_contents_id+1})""")
    cursor.connection.commit()

def delete_at_db(select, contents_id=-1, user_no=-1):
    if select == "contents":
        cursor.execute(f"delete from board where contents_id={contents_id}")
    elif select == "account":
        cursor.execute(f"delete from user where user_no={user_no}")
    cursor.connection.commit()

def edit_at_db(select, json):
    if select == "contents":
        cursor.execute(f"""update board set title="{json['title']}", contents="{json['contents']}" where contents_id={json['contents_id']}""")
    elif select == "account":
        cursor.execute(f"""update user set name="{json['username']}", password="{json['password']}" where user_no={json['user_no']}""")
    cursor.connection.commit()

def search_engine():
    pass