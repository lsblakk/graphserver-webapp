import sqlite3
import time
from flask import Flask, request, session, redirect, url_for, jsonify
from flask import abort, render_template, flash
from contextlib import closing
from sqlalchemy import create_engine, MetaData, Table

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

engine = create_engine(app.config['DATABASE_URI'], convert_unicode=True)
metadata = MetaData(bind=engine)

branches = Table('branches', metadata, autoload=True)

@app.before_request
def before_request():
    session['version'] = app.config['VERSION']

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def show_entries():
    branches = engine.execute('select * from branches')
    machines = engine.execute('select * from machines')
    return render_template('show_entries.html', branches=branches, machines=machines)

@app.route('/add_branch', methods=['POST'])
def add_branch():
    if not session.get('logged_in'):
        abort(401)
    # TODO - form validation here
    con = engine.connect()
    con.execute('insert into branches (id, name) values (NULL, %s)', request.form['branch_name'])
    flash('New branch %s was successfully inserted' % request.form['branch_name'])
    # return json here?
    return redirect(url_for('show_entries'))

@app.route('/add_machine', methods=['POST'])
def add_machine():
    if not session.get('logged_in'):
        abort(401)
    # TODO - form validation
    con = engine.connect()
    con.execute('insert into machines (id, os_id, is_throttling, cpu_speed, name, is_active, date_added) \
                values (NULL, %s, 0, NULL, %s, 1, %s)', [request.form['os_id'], request.form['machine_name'] ,int(time.time())])
    flash('New machine was successfully posted')
    # return json here?
    return redirect(url_for('show_entries'))

@app.route('/delete_machine', methods=['GET', 'POST', 'DELETE'])
def delete_machine():
    if not session.get('logged_in'):
        abort(401)
    # confirm delete
    # check id is valid, if not catch/flash error
    if request.method == 'POST':
        con = engine.connect()
        con.execute('delete from machines where id=%d' % int(request.form['id']))
        flash('Machine %d was successfully deleted' % int(request.form['id']))
    if request.method == 'DELETE':
        print request
        print dir(request)
    # return json here?
    if request.method == 'GET':
        print request
        print dir(request)
    return redirect(url_for('show_entries'))

@app.route('/delete_branch', methods=['POST'])
def delete_branch():
    if not session.get('logged_in'):
        abort(401)
    con = engine.connect()
    con.execute('delete from branches where id=%d' % int(request.form['id']))
    flash('Branch %s was successfully deleted' % request.form['branch_name'])
    # return json here?
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
