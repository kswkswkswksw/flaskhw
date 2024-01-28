from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta
from db import login_check, join_account, bbs_info, try_view_amount, write_up_at_db, delete_at_db, edit_at_db
from flask_socketio import SocketIO

import hashlib

app = Flask(__name__)
app.secret_key = 'admin'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)

@app.route('/', methods=["GET"])
def index():
    if 'username' in session:
        return render_template('index.html', name=session['username'])
    return render_template('login.html')

@app.route("/bbs", methods=['GET', "POST"])
def bbs():
    if request.method == 'GET':
        req = request.args.get('q')
        if req == None:
            return render_template("bbs.html", info=bbs_info(), sesscheck= 1 if 'username' in session else 0)
        log = bbs_info(req)[0]
        try_view_amount(req)
        session['current_view'] = req
        
        try:
            trigger = 1 if log[1] == session['user_no'] else 0
        except KeyError:
            trigger = 0 
        # 템플릿으로 보낼 변수가 많을 경우 json으로 가공후 사용을 추천
        return render_template("contents.html", trigger=trigger, title=log[2], name=log[0], contents=log[3], views=log[4])

@app.route('/write_up', methods=['GET', 'POST'])
def write_up():
    if 'username' in session:
        if request.method == 'POST':
            req = request.form
            write_up_at_db(json=req, user_no=session['user_no'],username=session['username'])
            return redirect(url_for('bbs'))
        return render_template("write_up.html", page_title='Write Up!', location='/write_up')
    return redirect(url_for('index'))

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if 'username' in session:
        return render_template('chat.html', name=session['username'])
    return redirect(url_for('index'))

socketio = SocketIO(app)

@socketio.on("event")
def event_handler(json):
	if "data" in json:
		if json["data"] == "Connect":
			socketio.emit("res", {"name":"", "message": "Connect new user"})
	else:
		socketio.emit("res", {"name": session['username'], "message": json['message']})
          
@app.route('/login', methods=["POST"])
def login():
    req = request.form
    info = login_check(req['id'], hashlib.sha256(req['password'].encode()).hexdigest())
    if info:
        session['username'] = info[2]
        session['user_no'] = info[3]
        session['current_view'] = -1
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_no', None)
    return redirect(url_for('index'))

@app.route('/join/<ajax>', methods=['GET','POST'])
def join(ajax):
    if ajax == "ajax":
        req = request.form
        join_account(req['id'], hashlib.sha256(req['password'].encode()).hexdigest(), req['username'])
        return redirect(url_for('index'))
    else:
        return render_template('join.html', page_title='join account for bbs', location="/join/ajax", trigger=1)
    
@app.route('/delete/<want>', methods=['POST'])
def delete(want):
    if want == "contents":
        delete_at_db(select=want, contents_id=session['current_view'])
    elif want == "account":
        delete_at_db(select=want, user_no=session['user_no'])
        return redirect(url_for('logout'))
    return redirect(url_for('bbs'))

@app.route('/edit/<want>', methods=['GET', 'POST'])
def edit(want):
    if want == "contents":
        if request.method == 'POST':
            req = request.form.to_dict() # ImmutableMultiDict change Default dict
            req['contents_id'] = int(session['current_view'])
            # print(req)
            edit_at_db(select=want, json=req)
            return redirect(url_for('bbs'))
        if request.method == 'GET':
            log = bbs_info(session['current_view'])[0]
            return render_template('write_up.html', page_title='Edit', title=log[2], contents=log[3], location='/edit/contents')
    elif want == "account":
        if request.method == 'POST':
            req = request.form.to_dict()
            req['user_no'] = session['user_no']
            req['password'] = hashlib.sha256(req['password'].encode()).hexdigest()
            edit_at_db(select=want, json=req)
            return redirect(url_for('index'))
        if request.method == 'GET':
            return render_template('join.html', page_title='Edit Account', location='/edit/account', trigger=0, username=session['username'])
            

