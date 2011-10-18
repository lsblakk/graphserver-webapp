import os, sys
sys.path.append('..')
import graphserver
import unittest
import tempfile
import json

class GraphserverTestCase(unittest.TestCase):

    def setUp(self):
        graphserver.app.config.from_object('config.TestConfig')
        self.app = graphserver.app.test_client()
        # create the sqlite db here?

    def tearDown(self):
        # delete everything in the db here or the db completely
        pass
    
    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No machines' in rv.data
        assert 'No branches' in rv.data

    def test_add_empty_branch_web(self):
        rv = self.app.post('/branches', data=dict(
            branch_name='',
            _method='insert'
        ), follow_redirects=True)
        assert 'Please enter a branch name' in rv.data

    def test_add_branch_web(self):
        rv = self.app.post('/branches', data=dict(
            branch_name='new_branch_web',
            _method='insert'
        ), follow_redirects=True)
        assert 'new_branch' in rv.data

    def test_delete_branch_web(self):
        rv = self.app.post('/branches', data=dict(
            id=2,
            _method='delete'
        ), follow_redirects=True)
        rv = self.app.get('/')
        assert 'No branches' in rv.data

    def test_delete_nonexistent_branch_json(self):
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results_pre = json.loads(resp.data)
        rv = self.app.post('/branches', data=dict(
            id=14,
            format='json',
            _method='delete'
        ), follow_redirects=True)
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_add_branch_json(self):
        rv = self.app.post('/branches', data=dict(
            branch_name='new_branch_json',
            format='json',
            _method='insert'
        ), follow_redirects=True)
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results['1'] == 'new_branch_json'

    def test_add_empty_branch_json(self):
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results_pre = json.loads(resp.data)
        rv = self.app.post('/branches', data=dict(
            branch_name='',
            format='json',
            _method='insert'
        ), follow_redirects=True)
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_delete_branch_json(self):
        rv = self.app.post('/branches', data=dict(
            id=1,
            format='json',
            _method='delete'
        ), follow_redirects=True)
        resp = self.app.get('/branches?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results == {'2': 'new_branch_web'}


    def test_add_machine_json(self):
        rv = self.app.post('/machines', data=dict(
            os_id=13,
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='new_machine_json',
            is_active=0,
            format='json',
            _method='insert'
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results['1'] == 'new_machine_json'

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
            _method='insert'
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
            _method='insert'
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_delete_machine_json(self):
        rv = self.app.post('/machines', data=dict(
            id=1,
            format='json',
            _method='delete'
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results = json.loads(resp.data)
        assert results == {'2': 'new_machine_web'}

    def test_delete_nonexistent_machine_json(self):
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_pre = json.loads(resp.data)
        rv = self.app.post('/machines', data=dict(
            id=14,
            format='json',
            _method='delete'
        ), follow_redirects=True)
        resp = self.app.get('/machines?format=json', follow_redirects=True)
        results_post = json.loads(resp.data)
        assert results_pre == results_post

    def test_add_machine_web(self):
        rv = self.app.post('/machines', data=dict(
            os_id='13',
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='new_machine_web',
            is_active=0,
            _method='insert'
        ), follow_redirects=True)
        assert 'new_machine_web' in rv.data

    def test_delete_machine_web(self):
        rv = self.app.post('/machines', data=dict(
            id=2,
            _method='delete'
        ), follow_redirects=True)
        rv = self.app.get('/')
        assert 'No machines' in rv.data

if __name__ == '__main__':
    unittest.main()