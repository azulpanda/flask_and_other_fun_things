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

@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries = entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	message = None
	current_users = []
	go = True
	if request.method == 'POST': 
		if not os.path.isfile('user.txt'):
			file = open('user.txt', 'w')
			file.close()
		with open('user.txt', 'r') as users_list:
			read_file = users_list.read()
			if read_file != "":
				current_users = json.loads(read_file)
			for i in current_users:
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
				with open('user.txt', 'w') as users_list:
					users_list.write(json.dumps(current_users))
				flash('You are signed up')
				return redirect(url_for('show_entries'))

	return render_template('signup.html', message = message)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	current_users = []
	match = False
	if request.method == 'POST':
		if os.path.isfile('user.txt'):
			with open('user.txt', 'r') as users_list:
				read_file = users_list.read()
				if read_file != "":
					current_users = json.loads(read_file)
				for i in current_users:
					if 'email' in i:
						if request.form['email'] == i['email']:
							match = True
							if i['password'] == request.form['password']:
								session['logged_in'] = True
								session['email'] = i['email']
								session['admin'] = i['admin']
								flash('You are logged in')
								return redirect(url_for('show_entries'))
							else:
								error = 'Invalid password'
		if not match:
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
	with open('user.txt', 'r') as data:
		user = json.loads(data.read())
	return render_template('user.html', user = user)


if __name__ == '__main__':
	init_db()
	app.run()
