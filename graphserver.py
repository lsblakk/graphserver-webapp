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
    app.branches = Table('branches', app.metadata, autoload=True)
    app.machines = Table('machines', app.metadata, autoload=True)
    
@app.before_request
def before_request():
    session['version'] = app.config['VERSION']
    init_db()

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def show_entries():
    branch_list = app.engine.execute('select * from branches')
    machine_list = app.engine.execute('select * from machines')
    return render_template('show_entries.html', branch_list=branch_list, machine_list=machine_list)

@app.route('/branches', methods=['GET', 'POST'])
def branches():
    # TODO - form validation
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            results = app.con.execute(app.branches.delete().where(app.branches.c.id == request.form['id']))
            flash('Branch %s was successfully deleted' % request.form['branch_name'])
        elif request.form['_method'] == "insert":
            results = app.con.execute(app.branches.insert(), name=request.form['branch_name'])
            flash('New branch %s was successfully added' % request.form['branch_name'])
    if request.method == 'GET' and request.args.get('format') == 'json':
        return jsonify(app.branches.select().execute().fetchall())
    if 'application/json' in request.headers.get('Accept', '') or request.form.get('format') == 'json':
        return jsonify(results)
    return redirect(url_for('show_entries'))

@app.route('/machines', methods=['GET', 'POST'])
def machines():
    # TODO - form validation
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            results = app.con.execute(app.machines.delete().where(app.machines.c.id == request.form['id']))
            flash("Machine '%s' was successfully deleted" % request.form['machine_name'])
        elif request.form['_method'] == "insert":
            results = app.con.execute(
                            app.machines.insert(), 
                            os_id=int(request.form['os_id']),
                            is_throttling=int(request.form['is_throttling']),
                            cpu_speed=request.form['cpu_speed'], 
                            name=request.form['machine_name'], 
                            is_active=int(request.form['is_active']), 
                            date_added=int(time.time())
                        )
            flash('New machine %s was successfully added' % request.form['machine_name'])
    if request.method == 'GET' and request.args.get('format') == 'json':
        machines = {}
        results = app.machines.select().execute().fetchall()
        for r in results:
            machines[r[0]] = r[4]
        return jsonify(machines)
    if 'application/json' in request.headers.get('Accept', '') or request.form.get('format') == 'json':
        return jsonify(results)
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
