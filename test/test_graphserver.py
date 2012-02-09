import os, sys
sys.path.append('..')
import graphserver
import unittest
import tempfile
import json
import subprocess

class GraphserverTestCase(unittest.TestCase):

    def setUp(self):
        graphserver.app.config.from_object('config.TestConfig')
        self.app = graphserver.app.test_client()
        # Remove the db and recreate it
        if os.path.exists('test_graphserver.sqlite'):
            os.remove('test_graphserver.sqlite')
            subprocess.call("sqlite3 test_graphserver.sqlite < test_db.sql", shell=True)
        else:
            subprocess.call("sqlite3 test_graphserver.sqlite < test_db.sql", shell=True)

    def test_empty_db(self):
        # Remove the db and recreate it
        if os.path.exists('test_graphserver.sqlite'):
            os.remove('test_graphserver.sqlite')
            subprocess.call("sqlite3 test_graphserver.sqlite < test_db.sql", shell=True)
        else:
            subprocess.call("sqlite3 test_graphserver.sqlite < test_db.sql", shell=True)
        rv = self.app.get('/')
        print rv.data
        assert 'No machines' in rv.data
        assert 'No branches' in rv.data

    def test_add_empty_branch_web(self):
        rv = self.app.post('/branch', data=dict(
            branch_name='',
        ), follow_redirects=True)
        assert 'Cannot add empty branch name' in rv.data

    def test_add_branch(self):
        rv = self.app.post('/branch', data=dict(
            branch_name='new_branch',
        ), follow_redirects=True)
        assert 'new_branch' in rv.data
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results['1'] == 'new_branch'

    def test_update_branch(self):
        rv = self.app.get('/')
        if 'No branches' in rv.data:
            print  "Need to add the branch first"
            rv = self.app.post('/branch', data=dict(
                branch_name='new_branch',
            ), follow_redirects=True)
        rv = self.app.get('/branches?format=json')
        results = json.loads(rv.data)
        print results
        rv = self.app.post('/branch', data=dict(
            branch_id=1,
            branch_name='updated_branch'),
            follow_redirects=True)
        rv = self.app.get('/branches?format=json')
        results = json.loads(rv.data)
        print results
        assert results['1'] == 'updated_branch'

    def test_add_empty_branch_json(self):
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results_pre = json.loads(resp.data)
        rv = self.app.post('/branch', data=dict(
            branch_name='',
            format='json',
        ), follow_redirects=True)
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_add_machine(self):
        rv = self.app.post('/machines', data=dict(
            os_id=13,
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='new_machine',
            is_active=0,
        ), follow_redirects=True)
        assert 'new_machine' in rv.data
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results['1'] == 'new_machine'

    def test_add_machine_with_blank_strings_json(self):
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_pre = json.loads(resp.data)
        rv = self.app.post('/machines', data=dict(
            os_id=12,
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='',
            is_active=0,
            format='json',
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_add_machine_with_non_numeric_json(self):
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_pre = json.loads(resp.data)
        rv = self.app.post('/machines', data=dict(
            os_id='OS',
            is_throttling='s',
            cpu_speed='',
            machine_name='',
            is_active='',
            format='json',
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_update_machine(self):
        resp = self.app.get('/', follow_redirects=True)
        if 'No machines' in resp.data:
            print "Need to insert a machine"
            rv = self.app.post('/machines', data=dict(
                os_id=13,
                is_throttling=1,
                cpu_speed=1.12,
                machine_name='new_machine',
                is_active=0,
            ), follow_redirects=True)
        rv = self.app.post('/machines', data=dict(
            machine_id=1,
            machine_name='updated_machine',
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results['1'] == 'new_machine'
    
if __name__ == '__main__':
    unittest.main()