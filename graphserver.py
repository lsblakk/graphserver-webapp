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
            # This branch exists, update the name
            branch_name, id = request.form.listvalues()
            # Validate user input
            if len(branch_name) != 0:
                results = app.con.execute(app.branches.update().where(app.branches.c.id==int(id[0])).values(
                    name=branch_name[0]))
                flash('Branch %s updated' % request.form['branch_id'])
                app.logger.info('Branch %s updated' % request.form['branch_id'])
            else:
                flash('Branch name cannot be blank, not updated')
                app.logger.info('Branch name cannot be blank, not updated')
    else:
        # New branch to try and insert - first validate input
        if len(request.form.get('branch_name')) == 0:
            flash('Error: Cannot add empty branch name')
            app.logger.error('Cannot add empty branch name')
        else:
            results = app.con.execute(app.branches.insert(), name=request.form['branch_name'])
            flash('New branch "%s" was successfully added' % request.form['branch_name'])
            app.logger.info('New branch "%s" was successfully added' % request.form['branch_name'])
    
    return redirect(url_for('show_entries'))

@app.route('/branch/<branch_id>&branch_name=<branch_name>', methods=['GET'])
def edit_branch(branch_id, branch_name):
    return render_template('update_entry.html', branch_id=branch_id, branch_name=branch_name)

@app.route('/branches', methods=['GET'])
def get_branches():
    if is_json():
        return jsonify(app.branches.select().execute().fetchall())
    return redirect(url_for('show_entries'))

@app.route('/machines/<machine_id>', methods=['POST'])
def edit_machine(machine_id):
    return render_template('update_entry.html', machine_id=machine_id,
        name=request.form.get('name'),
        os_id=request.form.get('os_id'),
        is_throttling=request.form.get('is_throttling'),
        is_active=request.form.get('is_active'),
        cpu_speed=request.form.get('cpu_speed'))

@app.route('/machines', methods=['POST'])
def update_machines():
    errors = False
    # Existing machine has and id
    if request.form.get('machine_id'):
        exists = app.con.execute(app.machines.select().where(app.machines.c.id == request.form['machine_id']))
        entry = exists.fetchone()
        if entry != None:            
            machine = Machine(id=request.form['machine_id'],name=request.form.get('machine_name'),
                os_id=request.form.get('os_id'),is_throttling=request.form.get('is_throttling'),
                is_active=request.form.get('is_active'),cpu_speed=request.form.get('cpu_speed'))
            if machine.valid:
                print "Machine is valid %s" % machine
                results = app.con.execute(app.machines.update().where(app.machines.c.id==int(request.form.get('machine_id'))).values(machine.toDict()))
                flash('Machine %s updated' % request.form['machine_id'])
                app.logger.info('Machine %s updated' % request.form['machine_id'])
            else:
                flash('Machine cannot be updated, some values are incorrect')
                app.logger.info('Machine cannot be updated, some values are incorrect')
    # Otherwise we are going to insert a new machine
    else:
        exists = app.con.execute(app.machines.select().where(app.machines.c.name == 
                    request.form['machine_name']))
        if exists.fetchone() != None:
            flash('Machine name "%s" exists, please enter a unique name' % request.form['machine_name'])
            app.logger.warning('Machine name "%s" exists, please enter a unique name', request.form['machine_name'])
            errors = True
        machine = Machine(name=request.form['machine_name'], is_throttling=request.form['is_throttling'],
            is_active=request.form['is_active'], cpu_speed=request.form['cpu_speed'], os_id = request.form['os_id'])
        if not errors and machine.valid:
            insert_values = machine.toDict()
            insert_values['date_added'] = int(time.time())
            results = app.con.execute(
                        app.machines.insert(), 
                        insert_values,
                    )
            flash('New machine "%s" was successfully added' % request.form['machine_name'])
            app.logger.info('New machine "%s" was successfully added' % request.form['machine_name'])
        elif not machine.valid:
            flash('Check machine values (name, cpu_speed, os_id) for correctness, no machine added.')
            app.logger.info('Check machine values (name, cpu_speed, os_id) for correctness, no machine added.')

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

class Machine(object):
    # Defaults: is_throttling = 0, is_active = 1 
    # If name or cpu_speed don't validate then valid is False
    def __init__(self, id=None, os_id=False, is_throttling=False, cpu_speed=False,
            name=False, is_active=False, valid=False):
            self.id = id
            if self.id != None:
                # fetch the existing machine
                exists = app.con.execute(app.machines.select().where(app.machines.c.id == id))
                machine = exists.fetchone()
                if machine != 0:
                    self.os_id = machine[1]
                    self.is_throttling = machine[2]
                    self.cpu_speed = machine[3]
                    self.name = machine[4]
                    self.is_active = machine[5]
                    self.valid = True
            else:   
                try:
                    self.os_id = int(os_id)
                except:
                    self.os_id = False
                if is_throttling in [0,1]:
                    self.is_throttling = is_throttling
                else:
                    self.is_throttling = 0
                try:
                    self.cpu_speed = float(cpu_speed)
                except:
                    self.cpu_speed = False
                self.name = name
                if is_active in [0,1]:
                    self.is_active = is_active
                else:
                    self.is_active = 1
                if len(self.name) != 0 and self.cpu_speed and self.os_id:
                    self.valid = True
                else:
                    self.valid = valid
    
    def __repr__(self):
        return str(self.toDict())
    
    def toDict(self):
        d = {
            'id': self.id,
            'os_id': self.os_id,
            'is_throttling': self.is_throttling,
            'is_active': self.is_active,
            'cpu_speed': self.cpu_speed,
            'name': self.name,
        }
        return d
        
if __name__ == '__main__':
    app.run()
