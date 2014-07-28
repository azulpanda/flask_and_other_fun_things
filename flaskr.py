import os
import sqlite3
import re
import json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)
users = []

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'flaskr.db'),
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database connection if there is none yet for the current application context."""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def get_user():
	user = []
	if not os.path.isfile('user.txt'):
			file = open('user.txt', 'w')
			file.close()
	with open('user.txt', 'r') as data:
		read_file = data.read()
		if read_file != "":
			user = json.loads(read_file)
	return user

@app.route('/')
def show_entries():
	entries = []
	if not os.path.isfile('entry.txt'):
		file = open('entry.txt', 'w')
		file.close()
	with open('entry.txt', 'r') as data:
		entries_list = data.read()
		if entries_list != "":
			entries = json.loads(entries_list)
	return render_template('show_entries.html', entries = entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if session['logged_in']:
		entries = []
		if not os.path.isfile('entry.txt'):
			file = open('entry.txt', 'w')
			file.close()
		with open('entry.txt', 'r') as data:
			entries_list = data.read()
			if entries_list != "":
				entries = json.loads(entries_list)
		new_entry = { 'num':len(entries), 'title':request.form['title'], 'text':request.form['text'], 'email':session['email'] }
		entries.append(new_entry)
		with open('entry.txt', 'w') as data:
			data.write(json.dumps(entries))
		flash('New entry was successfully posted')
	else:
		abort(401)
	return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	message = None
	current_users = []
	go = True
	if request.method == 'POST': 
		user = get_user()
		for i in user:
			if 'email' in i:
				if request.form['email'] == i['email']:
					message = "Existing email"
					go = False
		if go:	
			if not re.match("^[a-zA-z._0-9]+@[a-zA-Z0-9-]+\.(com|net|ac\.kr)$", request.form['email'] ):
				message = "Invalid email"
			elif not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,20}$", request.form['password'] ):
				message = "Invalid password"
			elif request.form['password'] != request.form['password_check']:
				message = "Passwords are different"
			else: 
				if 'admin' in request.form:
					new_user = { 'email':request.form['email'], 'password':request.form['password'], 'admin':True }
				else:
					new_user = { 'email':request.form['email'], 'password':request.form['password'], 'admin':False }
				current_users.append(new_user)	
				with open('user.txt', 'w') as data:
					data.write(json.dumps(current_users))
				flash('You are signed up')
				return redirect(url_for('show_entries'))

	return render_template('signup.html', message = message)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	user = []
	if request.method == 'POST':
		user = get_user()
		for i in user:
			if request.form['email'] == i['email']:
				if i['password'] == request.form['password']:
					session['logged_in'] = True
					session['email'] = i['email']
					session['admin'] = i['admin']
					flash('You are logged in')
					return redirect(url_for('show_entries'))
				else:
					error = 'Invalid password'
				break
		else:
			error = 'Invalid email. Sign up'
	return render_template('login.html', error = error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('password', None)
	session.pop('admin', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

@app.route('/user')
def user():
	user = []
	if not os.path.isfile('user.txt'):
			file = open('user.txt', 'w')
			file.close()
	with open('user.txt', 'r') as data:
		read_file = data.read()
		if read_file != "":
			user = json.loads(read_file)
	return render_template('user.html', user = user)

@app.route('/email_check', methods=['POST'])
def email_check():
	print 'hi'
	email = request.form['email']
	user = get_user()
	result = ""
	for i in user:
		if email == i['email']:
			result = "taken"
	return result

if __name__ == '__main__':
	init_db()
	app.run()
