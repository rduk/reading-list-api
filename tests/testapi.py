from tests import test_app, get_aws_data
from unittest import TestCase
import json

class TestIntegrations(TestCase):
    def setUp(self):
        self.app = test_app

    def test_homepage_status_code(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_homepage_content(self):
        resp = self.app.get('/')
        self.assertEqual(True, 'Welcome to Reading List Be API homepage' in str(resp.data))

    def test_books_endpoint_status_code(self):
        resp = self.app.get('/readlist/api/v1/books')
        self.assertEqual(resp.status_code, 200)

    def test_books_endpoint_content(self):
        resp = self.app.get('/readlist/api/v1/books')
        # get the actual content from aws source
        self.assertEqual(True, json.dumps(get_aws_data) in (json.dumps(resp.json)))

    def test_books_sort_name_endpoint_status_code(self):
        resp = self.app.get('/readlist/api/v1/books?sort=name')
        self.assertEqual(resp.status_code, 200)

    def test_books_sort_published_at_endpoint_status_code(self):
        resp = self.app.get('/readlist/api/v1/books?sort=published_at')
        self.assertEqual(resp.status_code, 200)

    def test_books_sort_invalid_key_endpoint(self):
        # testing <title> key in sorting param
        resp = self.app.get('/readlist/api/v1/books?sort=title')
        self.assertEqual(True, 'Sorting key <title> is not supported' in str(resp.data))

    def test_authors_endpoint_status_code(self):
        resp = self.app.get('/readlist/api/v1/authors')
        self.assertEqual(resp.status_code, 200)

    def test_invalid_endpoint_status_code(self):
        resp = self.app.get('/readlist/api/invalidurl')
        self.assertEqual(resp.status_code, 404)
