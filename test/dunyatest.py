import unittest

from compmusic.dunya.conn import _make_url


class DunyaTest(unittest.TestCase):
    def test_unicode(self):
        params = {"first": "%^grt"}
        url = _make_url("path", **params)
        self.assertEqual(url, 'http://dunya.compmusic.upf.edu/path?first=%25%5Egrt')
