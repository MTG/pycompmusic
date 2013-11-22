import unittest

from compmusic import tags

class TagTest(unittest.TestCase):
    def test_usul(self):
        t = "usul: something"
        self.assertEqual(True, tags.has_usul(t))
        self.assertEqual("something", tags.parse_usul(t))
        pass

    def test_makam(self):
        t = "makam: something"
        self.assertEqual(True, tags.has_makam(t))
        self.assertEqual("something", tags.parse_makam(t))

    def test_form(self):
        t = "form: something"
        self.assertEqual(True, tags.has_form(t))
        self.assertEqual("something", tags.parse_form(t))

    def test_raaga(self):
        t = "raaga1 bhairavi"
        self.assertEqual("bhairavi", tags.parse_raaga(t))

        t = "bhairavi raaga1"
        self.assertEqual("bhairavi", tags.parse_raaga(t))

        t = "raga kedaragaula"
        self.assertEqual("kedaragaula", tags.parse_raaga(t))

    def test_taala(self):
        t = "taala sankeerna jati triputa"
        self.assertEqual("sankeerna jati triputa", tags.parse_taala(t))
