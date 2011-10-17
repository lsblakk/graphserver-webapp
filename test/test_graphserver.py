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

    def tearDown(self):
        pass
    
    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No machines' in rv.data
        assert 'No branches' in rv.data

    def test_add_branch(self):
        rv = self.app.post('/branches', data=dict(
            branch_name='new_branch',
            format='json',
            _method='insert'
        ), follow_redirects=True)
        print rv.data

    def test_add_machine(self):
        rv = self.app.post('/machines', data=dict(
            os_id='13',
            is_throttling=1,
            cpu_speed=1.12,
            machine_name='new_machine',
            is_active=0,
            format='json',
            _method='insert'
        ), follow_redirects=True)
        print rv.data
    
    def test_delete_branch(self):
        rv = self.app.get('/')
        assert 'No branches' in rv.data

    def test_delete_machine(self):
        rv = self.app.get('/')
        assert 'No machines' in rv.data

if __name__ == '__main__':
    unittest.main()