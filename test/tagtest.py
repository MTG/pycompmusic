# -*- coding: utf-8 -*-
import unittest

from compmusic import tags

class MakamTagTest(unittest.TestCase):
    def test_usul(self):
        t = "usul: something"
        self.assertEqual(True, tags.has_usul(t))
        self.assertEqual((0, "something"), tags.parse_usul(t))

        t = "usul 3: durak evferi"
        self.assertEqual(True, tags.has_usul(t))
        self.assertEqual((3, "durak evferi"), tags.parse_usul(t))

        t = "usul:devr-i kebir"
        self.assertEqual(True, tags.has_usul(t))
        self.assertEqual((0, "devr-i kebir"), tags.parse_usul(t))

        t = "usul serbest"
        self.assertEqual(True, tags.has_usul(t))
        self.assertEqual((0, "serbest"), tags.parse_usul(t))

        t = "usul : evfer"
        self.assertEqual(True, tags.has_usul(t))
        self.assertEqual((0, "evfer"), tags.parse_usul(t))

    def test_makam(self):
        t = "makam: something"
        self.assertEqual(True, tags.has_makam(t))
        self.assertEqual((0, "something"), tags.parse_makam(t))

        t = "makam1: something"
        self.assertEqual(True, tags.has_makam(t))
        self.assertEqual((1, "something"), tags.parse_makam(t))

        t = "makam:acemaşiran"
        self.assertEqual(True, tags.has_makam(t))
        self.assertEqual((0, "acemaşiran"), tags.parse_makam(t))

        t = u"makam : uşşak"
        self.assertEqual(True, tags.has_makam(t))
        self.assertEqual((0, u"uşşak"), tags.parse_makam(t))

        t = u"makam 2: bestenigar"
        self.assertEqual(True, tags.has_makam(t))
        self.assertEqual((2, u"bestenigar"), tags.parse_makam(t))

    def test_form(self):
        t = "form: something"
        self.assertEqual(True, tags.has_makam_form(t))
        self.assertEqual((0, "something"), tags.parse_makam_form(t))

        t = "form:beste"
        self.assertEqual(True, tags.has_makam_form(t))
        self.assertEqual((0, "beste"), tags.parse_makam_form(t))

        t = "form 1: peşrev"
        self.assertEqual(True, tags.has_makam_form(t))
        self.assertEqual((1, "peşrev"), tags.parse_makam_form(t))
        
        t = "form: Rumelitürküsü"
        self.assertEqual(True, tags.has_makam_form(t))
        self.assertEqual((0, "Rumelitürküsü"), tags.parse_makam_form(t))

    def test_group_makam_tags(self):
        makams = [(0, "beyati")]
        forms = [(0, "peşrev")]
        usuls = [(0, "hafif")]

        groups = tags.group_makam_tags(makams, forms, usuls)
        self.assertEqual(1, len(groups))
        g = groups[0]
        self.assertEqual("beyati", g["makam"])
        self.assertEqual("peşrev", g["form"])
        self.assertEqual("hafif", g["usul"])

        # Test two sets of tags
        makams = [(0, "Zilkeş"), (1, "Uşşak")]
        forms = [(0, "Sirto"), (1, "Peşrev")]
        usuls = [(0, "Sofyan"), (1, "Remel")]
        groups = tags.group_makam_tags(makams, forms, usuls)
        self.assertEqual(2, len(groups))
        g = groups[0]
        self.assertEqual("Zilkeş", g["makam"])
        g = groups[1]
        self.assertEqual("Uşşak", g["makam"])
        self.assertEqual("Peşrev", g["form"])
        self.assertEqual("Remel", g["usul"])

        # Missing a tag on the last number
        makams = [(0, "Zilkeş")]
        forms = [(0, "Sirto"), (1, "Peşrev")]
        usuls = [(0, "Sofyan"), (1, "Remel")]
        groups = tags.group_makam_tags(makams, forms, usuls)
        self.assertEqual(2, len(groups))
        g = groups[0]
        self.assertEqual("Zilkeş", g["makam"])
        g = groups[1]
        self.assertTrue("makam" not in g)
        self.assertEqual("Peşrev", g["form"])
        self.assertEqual("Remel", g["usul"])

        # Missing a tag in the middle,
        # also, tags aren't in order
        makams = [(0, "Hisar"), (2, "Hicazeyn")]
        forms = [(1, "Kanto"), (2, "Destan")]
        usuls = [(0, "Zafer"), (1, "Sofyan"), (2, "Remel")]
        groups = tags.group_makam_tags(makams, forms, usuls)
        self.assertEqual(3, len(groups))
        g = groups[0]
        self.assertTrue("makam" in g)
        self.assertTrue("usul" in g)
        self.assertTrue("form" not in g)
        g = groups[1]
        self.assertTrue("makam" not in g)
        self.assertTrue("usul" in g)
        self.assertTrue("form" in g)
        g = groups[2]
        self.assertTrue("makam" in g)
        self.assertTrue("usul" in g)
        self.assertTrue("form" in g)

        # Some missing begining, some end - there should
        # be 2 sets, but max(len) is only 1
        makams = [(0, "Hisar")]
        forms = [(1, "Destan")]
        usuls = [(0, "Zafer")]
        groups = tags.group_makam_tags(makams, forms, usuls)
        self.assertEqual(2, len(groups))
        g = groups[0]
        self.assertTrue("makam" in g)
        self.assertTrue("usul" in g)
        self.assertTrue("form" not in g)
        g = groups[1]
        self.assertTrue("makam" not in g)
        self.assertTrue("usul" not in g)
        self.assertTrue("form" in g)

class CarnaticTagTest(unittest.TestCase):
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

class HindustaniTagTest(unittest.TestCase):
    def test_raag(self):
        t = "raga1:abhogi"
        self.assertEqual(True, tags.has_raag(t))
        self.assertEqual((1, "abhogi"), tags.parse_raag(t))

        t = "raga1: abhogi"
        self.assertEqual(True, tags.has_raag(t))
        self.assertEqual((1, "abhogi"), tags.parse_raag(t))

    def test_taal(self):
        t = "tala2:teental"
        self.assertEqual(True, tags.has_taal(t))
        self.assertEqual((2, "teental"), tags.parse_taal(t))

        t = "tala2: teental"
        self.assertEqual(True, tags.has_taal(t))
        self.assertEqual((2, "teental"), tags.parse_taal(t))

    def test_laya(self):
        t = "laya: drut"
        self.assertEqual(True, tags.has_laya(t))
        self.assertEqual((0, "drut"), tags.parse_laya(t))

        t = "laya1: madhya"
        self.assertEqual(True, tags.has_laya(t))
        self.assertEqual((1, "madhya"), tags.parse_laya(t))


    def test_form(self):
        t = u"form: Jugalbandī"
        self.assertEqual(True, tags.has_hindustani_form(t))
        self.assertEqual((0, u"Jugalbandī"), tags.parse_hindustani_form(t))
