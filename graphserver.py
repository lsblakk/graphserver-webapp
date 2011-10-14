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

@app.route('/branches', methods=['GET', 'POST'])
def branches():
    # TODO - form validation here
    con = engine.connect()
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            con.execute('delete from branches where id=%d' % int(request.form['id']))
            flash('Branch %s was successfully deleted' % request.form['branch_name'])
            return redirect(url_for('show_entries'))
        else:
            con.execute('insert into branches (id, name) values (NULL, %s)', request.form['branch_name'])
            flash('New branch %s was successfully added' % request.form['branch_name'])
    # return json here?
    return redirect(url_for('show_entries'))

@app.route('/machines', methods=['GET', 'POST'])
def machines():
    # TODO - form validation
    con = engine.connect()
    if request.method == 'POST':
        if request.form['_method'] == "delete":
            con.execute('delete from machines where id=%d' % int(request.form['id']))
            flash("Machine '%s' was successfully deleted" % request.form['machine_name'])
        else:
            con.execute('insert into machines (id, os_id, is_throttling, cpu_speed, name, is_active, date_added) \
                        values (NULL, %s, 0, NULL, %s, 1, %s)', [request.form['os_id'], request.form['machine_name'] ,int(time.time())])
            flash('New machine was successfully added')
    # return json here?
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
