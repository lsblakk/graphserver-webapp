import sqlite3
import time
from flask import Flask, request, session, redirect, url_for, jsonify
from flask import abort, render_template, flash
from contextlib import closing
from sqlalchemy import create_engine, MetaData, Table

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

def init_db():
    app.engine = create_engine(app.config['DATABASE_URI'], convert_unicode=True)
    app.metadata = MetaData(bind=app.engine)
    app.con = app.engine.connect()
    
@app.before_request
def before_request():
    session['version'] = app.config['VERSION']
    init_db()

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def show_entries():
    branches = app.engine.execute('select * from branches')
    machines = app.engine.execute('select * from machines')
    return render_template('show_entries.html', branches=branches, machines=machines)

@app.route('/branches', methods=['GET', 'POST'])
def branches():
    # TODO - form validation
    print request.form
    if request.method == 'POST':
        print request.form
        if request.form['_method'] == "delete":
            print 'delete'
            results = app.con.execute('delete from branches where id=%d' % int(request.form['id']))
            flash('Branch %s was successfully deleted' % request.form['branch_name'])
        elif request.form['_method'] == "insert":
            print 'insert'
            results = app.con.execute('insert into branches(id, name) values (NULL, %s)', request.form['branch_name'])
            flash('New branch %s was successfully added' % request.form['branch_name'])
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify(results)
    if request.form.get('format') == 'json':
        return jsonify(results)
    return redirect(url_for('show_entries'))

@app.route('/machines', methods=['GET', 'POST'])
def machines():
    # TODO - form validation
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            results = app.con.execute('delete from machines where id=%d' % int(request.form['id']))
            flash("Machine '%s' was successfully deleted" % request.form['machine_name'])
        elif request.form['_method'] == "insert":
            results = app.con.execute('insert into machines(id, os_id, is_throttling, cpu_speed, name, is_active, date_added) \
                        values (NULL, %s, %s, %s, %s, %s, %s)', [request.form['os_id'], request.form['is_throttling'],
                        request.form['cpu_speed'], request.form['machine_name'], request.form['is_active'], int(time.time())])
            flash('New machine was successfully added')
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify(results)
    if request.form.get('format') == 'json':
        return jsonify(results)
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
