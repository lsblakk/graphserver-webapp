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
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            stmt = "delete from branches where id = %d" % int(request.form['id'])
            results = app.con.execute(stmt)
            flash('Branch %s was successfully deleted' % request.form['branch_name'])
        elif request.form['_method'] == "insert":
            stmt = "insert into branches(id, name) values (NULL, '%s')" % request.form['branch_name']
            results = app.con.execute(stmt)
            flash('New branch %s was successfully added' % request.form['branch_name'])
    if 'application/json' in request.headers.get('Accept', '') or request.form.get('format') == 'json':
        return jsonify(results)
    return redirect(url_for('show_entries'))

@app.route('/machines', methods=['GET', 'POST'])
def machines():
    # TODO - form validation
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            stmt = "delete from machines where id = %d" % int(request.form['id'])
            results = app.con.execute(stmt)
            flash("Machine '%s' was successfully deleted" % request.form['machine_name'])
        elif request.form['_method'] == "insert":
            stmt = "insert into machines(id, os_id, is_throttling, cpu_speed, name, is_active, date_added) \
                        values (NULL, %d, %d, %s, '%s', %d, %d)" % (int(request.form['os_id']), int(request.form['is_throttling']),
                        request.form['cpu_speed'], request.form['machine_name'], int(request.form['is_active']), int(time.time()))
            results = app.con.execute(stmt)
            flash('New machine %s was successfully added' % request.form['machine_name'])
    if 'application/json' in request.headers.get('Accept', '') or request.form.get('format') == 'json':
        return jsonify(results)
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
