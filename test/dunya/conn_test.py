#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import unittest

from compmusic.dunya.conn import _make_url


class ConnTest(unittest.TestCase):
    def test_make_url(self):
        params = {"first": "%^grtà"}
        url = _make_url("path", **params)
        self.assertEqual(url, 'http://dunya.compmusic.upf.edu/path?first=%25%5Egrt%C3%A0')
