from flask import Flask, render_template, session,request,redirect,url_for
from homeworkdb import create_account, list_info
from flask_socketio import SocketIO

app=Flask(__name__)
app.secret_key='admin'

@app.route('/',methods=['GET','POST'])
def userlist():
    return render_template('housework.html')





@app.route('/hw_create',methods=['GET','POST'])
def printlist():
    
        
    return render_template('hw_create.html')
    
    




@app.route('/homeworkindex',methods=['GET','POST'])
def printall():
    if request.method=='POST':
        req=request.form
        create_account(req['user_name'],req['user_id'],req['user_psw'])
    
    
    
        
        
        

    return render_template('homeworkindex.html',info=list_info())

