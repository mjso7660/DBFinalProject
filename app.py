from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_socketio import SocketIO
import user
import chatroom
import chat
import json as js
import login
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
username = ''


@app.route('/')
def init():
	#print(session)
	if 'username' in session:
		return redirect(url_for('usermain',username=session['username']))
	else:
		return redirect(url_for('login'))

#TODO change name of login to register b/c login imported
@app.route('/login', methods=['Get','POST'])
def login():
	print('test')
	# < --------------------  ADDED CODE ----------------------->
	#if 'username' in session:
	#	redirect(url_for('usermain',username=session['username']))
	# < --------------------  ADDED CODE ----------------------->        
	error = None
	#print('--------------------------{}------------------'.format(request.form))
	if request.method == 'POST':
		#TODO: If signing UP
		username = request.form['username']
		password = request.form['password']
		if request.form['email']:
			password2 = request.form['password2']
			if password != password2:
				flash('Passwords dont match')
				error = "Passwords don't match"
			else:
				if user.insertAccount(username, password) is 'DuplicateKeyError':
					error = 'Username exists'
		#If signin IN
		else:
			#print(username,password)
			check = user.checkPassword(username, password)
			if not check:
				error = 'Incorrect username/password'
			else:
				session['username'] = username
				return redirect(url_for('usermain',username=session['username']))
	return render_template('register.html', error=error)

@app.route('/index/<username>')
def usermain(username, methods=['GET', 'POST']):
	u = user.getUser(session['username'])
	#cr = chatroom.getN(u,20)
	# for x in cr:
		# #print(x)
		# cs = chat.getChats(u, x, 20)
		# for c in cs:
			# #print(c)
	#print('hello world')
	return render_template('chat.html')


def messageReceived(methods=['GET', 'POST']):
	print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
	#print('received my event: ' + str(json))
	u = user.getUser(session['username'])
	cr = chatroom.getN(u,20)
	l = []
	for x in cr:
		l.append(x)
	chat.insertChat(u,l[session['index']],json['message'])
	socketio.emit('my response', json, callback=messageReceived)

@socketio.on('search')
def search(json, methods=['GET', 'POST']):
	u = user.getUser(session['username'])
	cr = chatroom.getN(u,20)
	l = []
	for x in cr:
		l.append(x)
	#print(json['message'])

	chat_dat = chat.searchChat(u,l[session['index']],json['message'])
	socketio.emit('message_history',chat_dat)

@socketio.on('boot')
def boot(json, methods=['GET', 'POST']):
	print(11111111111111)
	u = user.getUser(session['username'])
	cr = chatroom.getN(u,20)
	l = []
	for x in cr:
		l.append(chatroom.getInfo(x))
	#print(l)
	msg = {'data':l,'user':session['username']}
	socketio.emit('update_list',process_json(l),callback=messageReceived)

@socketio.on('test')
def test(json, methods=['GET', 'POST']):
	session['index'] = json['data']
	print(session['index'])
	u = user.getUser(session['username'])
	cr = chatroom.getN(u,20)
	l = []
	for x in cr:
		l.append(x)
	try:
		chat_data = chat.getChats(u,l[session['index']],20)
		socketio.emit('message_history',process_json(chat_data), callback=messageReceived)
	except:
		return

@socketio.on('add')
def add(json,methods=['GET','POST']):
	user_to_add = json['message'].split(',')
	
	# impossible if username not in chat
	if session['username'] not in user_to_add:
		return

	users = []
	#TODO: no user found
	for each in user_to_add:
		result = user.myusers.find_one({'username':each})
		if result is None:
			break
		#user found
		else:
			users.append(result['_id'])
			#create new chat room
			
	if result is None:
		socketio.emit('no_user',{'name':each})
		return
	else:
		chatroom.createChatroom('1', '1', users)


@app.route('/logout')
def logout():
	print(111111111111111)
	session.clear()
	return redirect(url_for('login'))

@socketio.on('log_out')
def log_out(json):
	logout()

def process_json(data):
	return_val = {'user':session['username'],'data':data}
	return return_val

if __name__ == '__main__':
	socketio.run(app, debug=True)

