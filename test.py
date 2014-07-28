from flask import session

session['logged_in'] = True

print session['logged_in']
