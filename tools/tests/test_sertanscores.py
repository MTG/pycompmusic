# -*- coding: utf-8 -*-
import unittest
import sertanscores

class MatchTest(unittest.TestCase):
    m = sertanscores.MakamScore(None, None, None, None)

    def test_honorific(self):
        self.assertTrue(self.m.match("Tatyos", "Tatyos Efendi"))
        #self.assertTrue(self.m.match("Tatyos", "Tatyos Ekserciyan"))
        self.assertTrue(self.m.match("Tateos", "Tatyos"))

        #self.assertTrue(self.m.match("Nevres", "Nevres Orhon"))
        self.assertTrue(self.m.match("Udi Nevres", "Udi Nevres Bey"))
        self.assertTrue(self.m.match("Nevres", "Udi Nevres Bey"))

        #self.assertTrue(self.m.match(u"Hafız Kemalettin Gürses", u"Hafız Kemalettin"))
        self.assertTrue(self.m.match(u"Hafız Kemal Bey", u"Hafız Kemal"))
        #self.assertTrue(self.m.match(u"Kemal Gürses", u"Kemal"))
        #self.assertTrue(self.m.match(u"Kemal Gürses", u"Kemalettin"))

        self.assertTrue(self.m.match("Udi Yorgo Bacanos", "Yorgo Bacanos"))
        self.assertTrue(self.m.match("Yorgo Bacanos", "Yorgo Bacanos Efendi"))
        #self.assertTrue(self.m.match("Yorgo Bacanos", "Yorgo Efendi"))
        self.assertTrue(self.m.match("Udi Yorgo", "Yorgo"))

        self.assertTrue(self.m.match("Buhurizade Mustafa Efendi", "Buhurizade Mustafa"))

    def test_characters(self):
        self.assertTrue(self.m.match(u"Şedd-i Arabân Peşrev", u"sedaraban Peşrev"))

    def test_unicode(self):
        self.assertTrue(self.m.match(u"Hafız Kemalettin Gürses", "Hafiz Kemalettin Gurses"))

    def test_ending(self):
        self.assertTrue(self.m.match("Saz Semaisi", "Sazsemaisi"))
        self.assertTrue(self.m.match("Saz Semaisi", "Saz Semai"))
        self.assertTrue(self.m.match("Sazsemaisi", "Saz Semai"))
        self.assertTrue(self.m.match("Sezsemai", "Saz Semai"))
        self.assertTrue(self.m.match("Sezsemai", "Sazsemaisi"))

    def test_distance(self):
        self.assertTrue(self.m.match("Nihavent Sazsemaisi", "Nihavend Saz Semai"))
        self.assertTrue(self.m.match("Mesut Cemil Bey", "Mesud Cemil"))
        self.assertTrue(self.m.match("", ""))
        self.assertTrue(self.m.match("", ""))

