import sqlite3
import time
from flask import Flask, request, redirect, url_for, jsonify
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

def is_json():
    if 'application/json' in request.headers.get('Accept', ''):
        return True
    if request.args.get('format') == 'json':
        return True
    return False
 
@app.before_request
def before_request():
    init_db()

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def show_entries():
    branch_list = app.engine.execute('select * from branches')
    machine_list = app.engine.execute('select * from machines')
    version = app.config['VERSION']
    return render_template('show_entries.html', branch_list=branch_list, 
                            machine_list=machine_list, version=version)

@app.route('/branches', methods=['GET', 'POST'])
def branches():
    if request.method == 'POST':
        if request.form.get('_method', False):
            if request.form['_method'] == "delete":
                exists = app.con.execute(app.branches.select().where(app.branches.c.id == request.form['id']))
                if exists.returns_rows:
                    results = app.con.execute(app.branches.delete().where(app.branches.c.id == request.form['id']))
                    flash('Branch %s was successfully deleted' % request.form['branch_name'])
        else:
            exists = app.con.execute(app.branches.select().where(app.branches.c.name == request.form['branch_name']))
            if exists.fetchone() != None:
                flash('Branch name exists, please enter a unique name')
            elif request.form['branch_name'] == '':
                flash('Please enter a branch name')
            else:
                results = app.con.execute(app.branches.insert(), name=request.form['branch_name'])
                flash('New branch %s was successfully added' % request.form['branch_name'])
    if is_json():
        return jsonify(app.branches.select().execute().fetchall())
    return redirect(url_for('show_entries'))

@app.route('/machines', methods=['GET', 'POST'])
def machines():
    if request.method == 'POST':
        if request.form.get('_method', False):
            if request.form['_method'] == "delete":
                exists = app.con.execute(app.machines.select().where(app.machines.c.id == request.form['id']))
                if exists.returns_rows:
                    results = app.con.execute(app.machines.delete().where(app.machines.c.id == request.form['id']))
                    flash("Machine '%s' was successfully deleted" % request.form['machine_name'])
        else:
            errors = False
            for key,value in request.form.items():
                if key == 'machine_name':
                    exists = app.con.execute(app.machines.select().where(app.machines.c.name == request.form['machine_name']))
                    if exists.fetchone() != None:
                        flash('Machine name exists, please enter a unique name')
                        errors = True
                    elif value == '':
                        flash('Please provide a machine name')
                        errors = True
                elif key in ('os_id', 'is_throttling', 'cpu_speed', 'is_active'):
                    try:
                        i = float(value)
                    except ValueError, TypeError:
                        flash('%s must have a numeric value' % key)
                        errors = True
            if not errors:
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
    if is_json():
        machines = {}
        results = app.machines.select().execute().fetchall()
        for r in results:
            machines[r[0]] = r[4]
        return jsonify(machines)
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
