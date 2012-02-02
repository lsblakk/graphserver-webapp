import sqlite3
import time
from flask import Flask, request, redirect, url_for, jsonify
from flask import abort, render_template, flash
from contextlib import closing
from sqlalchemy import create_engine, MetaData, Table
import logging, logging.handlers

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

#### LOGGING
format = logging.Formatter(fmt="%(asctime)s-%(levelname)s-%(funcName)s: %(message)s")
handler = logging.handlers.RotatingFileHandler(app.config['LOGFILE'], maxBytes=50000, backupCount=5)
handler.setFormatter(format)
app.logger.addHandler(handler)

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

@app.route('/branch', methods=['POST'])
def update_branch():
    if request.form.get('branch_id'):
        exists = app.con.execute(app.branches.select().where(app.branches.c.id == request.form['branch_id']))
        if exists.fetchone() != None:
            # This branch exists, update the info
            print "Branch exists"
            branch_name, id = request.form.listvalues()
            results = app.con.execute(app.branches.update().where(app.branches.c.id==int(id[0])).values(name=branch_name[0]))
            flash('Branch %s updated' % request.form['branch_id'])
            app.logger.info('Branch %s updated' % request.form['branch_id'])
    else:
        # New branch to be inserted
        print "New branch to be inserted"
        results = app.con.execute(app.branches.insert(), name=request.form['branch_name'])
        flash('New branch "%s" was successfully added' % request.form['branch_name'])
        app.logger.info('New branch "%s" was successfully added' % request.form['branch_name'])
    
    if is_json():
        return jsonify(app.branches.select().execute().fetchall())
    return redirect(url_for('show_entries'))

@app.route('/branch/<branch_id>?<branch_name>', methods=['POST'])
def edit_branch(branch_id, branch_name):
    print branch_name
    return render_template('update_entry.html', branch_id=branch_id, branch_name=branch_name)

@app.route('/branches', methods=['GET'])
def get_branches():
    if is_json():
        return jsonify(app.branches.select().execute().fetchall())
    return redirect(url_for('show_entries'))

@app.route('/machines/<machine_id>?<machine_name>?<os_id>?<is_throttling>?<is_active>', methods=['POST'])
def edit_machine(machine_id, machine_name, os_id, is_throttling, is_active):
    print machine_name
    return render_template('update_entry.html', machine_id=machine_id, machine_name=machine_name, os_id=os_id, is_throttling=is_throttling, is_active=is_active)

@app.route('/machines', methods=['POST'])
def update_machines():
    if request.form.get('machine_id'):
        exists = app.con.execute(app.machines.select().where(app.machines.c.id == request.form['machine_id']))
        errors = False
        if exists.fetchone() != None:
            print "Machine exists"
            print request.form.items()
            results = app.con.execute(
                app.machines.update().where(app.machines.c.id==int(request.form.get('machine_id'))).values(
                name=request.form.get('machine_name'),
                os_id=int(request.form.get('os_id')),
                is_throttling=int(request.form.get('is_throttling')),
                is_active=int(request.form.get('is_active')),
            ))
            flash('Machine %s updated' % request.form['machine_id'])
            app.logger.info('Machine %s updated' % request.form['machine_id'])
    else:
        for key,value in request.form.items():
            if key == 'machine_name':
                exists = app.con.execute(app.machines.select().where(app.machines.c.name == request.form['machine_name']))
                if exists.fetchone() != None:
                    flash('Machine name "%s" exists, please enter a unique name' % request.form['machine_name'])
                    app.logger.warning('Machine name "%s" exists, please enter a unique name', request.form['machine_name'])
                    errors = True
                elif value == '':
                    flash('Machine name cannot be blank')
                    app.logger.warning('Machine name cannot be blank')
                    errors = True
            elif key in ('os_id', 'is_throttling', 'cpu_speed', 'is_active'):
                try:
                    i = float(value)
                except ValueError, TypeError:
                    flash('"%s" must be a numeric value' % key)
                    app.logger.warning('"%s" must be a numeric value' % key)
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
            flash('New machine "%s" was successfully added' % request.form['machine_name'])
            app.logger.info('New machine "%s" was successfully added' % request.form['machine_name'])
    if is_json():
        machines = {}
        results = app.machines.select().execute().fetchall()
        for r in results:
            machines[r[0]] = r[4]
        return jsonify(machines)
    return redirect(url_for('show_entries'))  

@app.route('/machines', methods=['GET'])
def get_machines():
    if is_json():
        machines = {}
        results = app.machines.select().execute().fetchall()
        for r in results:
            machines[r[0]] = r[4]
        return jsonify(machines)
    return redirect(url_for('show_entries'))    

if __name__ == '__main__':
    app.run()
