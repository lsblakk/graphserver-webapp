import os, sys
sys.path.append('..')
import graphserver
import unittest
import tempfile

class GraphserverTestCase(unittest.TestCase):

    def setUp(self):
        graphserver.app.config.from_object('config.TestConfig')
        graphserver.app.config['TESTING'] = True
        self.app = graphserver.app.test_client()
        # create the sqlite db here?

    def tearDown(self):
        # delete everything in the db here or the db completely
        pass
    
    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No machines' in rv.data
        assert 'No branches' in rv.data

    def test_add_branch_web(self):
        rv = self.app.post('/branches', data=dict(
            branch_name='new_branch',
            _method='insert'
        ), follow_redirects=True)
        assert 'new_branch' in rv.data

    def test_delete_branch_web(self):
        rv = self.app.post('/branches', data=dict(
            id=1,
            _method='delete'
        ), follow_redirects=True)
        rv = self.app.get('/')
        assert 'No branches' in rv.data

    def test_add_branch_json(self):
        rv = self.app.post('/branches', data=dict(
            branch_name='new_branch',
            format='json',
            _method='insert'
        ), follow_redirects=True)
        print rv.data
        assert 'OK' in rv.data

    def test_delete_branch_json(self):
        rv = self.app.post('/branches', data=dict(
            id=2,
            format='json',
            _method='delete'
        ), follow_redirects=True)
        print rv.data
        assert 'OK' in rv.data

    def test_add_machine_json(self):
        rv = self.app.post('/machines', data=dict(
            os_id='13',
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='new_machine1',
            is_active=0,
            format='json',
            _method='insert'
        ), follow_redirects=True)
        print rv.data
        assert 'OK' in rv.data

    def test_delete_machine_json(self):
        rv = self.app.post('/machines', data=dict(
            id=1,
            format='json',
            _method='delete'
        ), follow_redirects=True)
        print rv.data
        assert 'OK' in rv.data

    def test_add_machine_web(self):
        rv = self.app.post('/machines', data=dict(
            os_id='13',
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='new_machine2',
            is_active=0,
            _method='insert'
        ), follow_redirects=True)
        assert 'new_machine2' in rv.data

    def test_delete_machine_web(self):
        rv = self.app.post('/machines', data=dict(
            id=2,
            _method='delete'
        ), follow_redirects=True)
        rv = self.app.get('/')
        assert 'No machines' in rv.data

if __name__ == '__main__':
    unittest.main()