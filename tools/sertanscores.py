#!/usr/bin/python
# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
# 
# This file is part of Dunya
# 
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from __future__ import print_function
import sys
import os
import argparse
import collections
import unidecode
import shutil
import random
import functools32
import json
import string

import Levenshtein
import re

import compmusic.file
import compmusic.musicbrainz
import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

class MakamScore(object):
    mapping = collections.defaultdict(list)
    targetdir = "results"

    def __init__(self, scores, pdfs, midis, audio):
        self.scores = scores
        self.pdfs = pdfs
        self.midis = midis
        self.audio = audio
        if self.audio:
            self.map_files_to_recording(self.audio)

    def map_files_to_recording(self, source_dir):
        if os.path.exists("recording_to_file.json"):
            self.mapping = json.load(open("recording_to_file.json"))
            return
        for root, dirs, files in os.walk(source_dir):
            if len(files):
                for f in files:
                    fname = os.path.join(root, f)
                    if compmusic.file.is_mp3_file(fname):
                        metadata = compmusic.file.file_metadata(fname)
                        recordingid = metadata["meta"]["recordingid"]
                        if recordingid:
                            self.mapping[recordingid].append(fname)
        json.dump(self.mapping, open("recording_to_file.json", "w"))

    def save_scores(self, fname, recordingids):
        # make a dir based on fname
        target = os.path.join(self.targetdir, fname)
        try:
            os.makedirs(target)
        except:
            pass
        try:
            shutil.copy(os.path.join(self.scores, fname+".txt"), target)
        except IOError:
            pass
        try:
            shutil.copy(os.path.join(self.pdfs, fname+".pdf"), target)
        except IOError:
            pass
        try:
            shutil.copy(os.path.join(self.midis, fname+".mid"), target)
        except IOError:
            pass

        for recid in recordingids:
            for fname in self.mapping.get(recid, []):
                name = os.path.basename(fname)
                n, ext = os.path.splitext(name)
                if os.path.exists(os.path.join(target, n)):
                    sourcedir = os.path.dirname(fname)
                    rand = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
                    ndir = "%s_%s" % (n, rand)
                    newname = "%s%s" % (ndir, ext)
                    newdest = os.path.join(target, ndir, newname)
                    try:
                        os.makedirs(os.path.dirname(newdest))
                    except:
                        pass
                    print(name, "exists, copying", target, "to", newname, "instead")
                    shutil.copy(fname, newdest)
                else:
                    innertarget = os.path.join(target, n)
                    try:
                        os.makedirs(innertarget)
                    except:
                        pass
                    shutil.copy(fname, innertarget)

    @functools32.lru_cache(2000)
    def get_performance_credit_for_recording(self, recordingid):
        recording = mb.get_recording_by_id(recordingid, includes=["releases"])
        recording = recording["recording"]
        ret = []
        for release in recording.get("release-list", []):
            relid = release["id"]
            mbrelease = mb.get_release_by_id(relid, includes=["artist-credits", "recordings"])
            mbrelease = mbrelease["release"]
            for medium in mbrelease.get("medium-list", []):
                for track in medium.get("track-list", []):
                    if track["recording"]["id"] == recordingid:
                        ret.append(track["recording"]["artist-credit-phrase"])
        return list(set(ret))

    @functools32.lru_cache(2000)
    def aliases_for_artist(self, artistid):
        a = mb.get_artist_by_id(artistid, includes=["aliases"])
        a = a["artist"]
        ret = []
        for alias in a.get("alias-list", []):
            ret.append(alias["alias"])
        return list(set(ret))

    @functools32.lru_cache(2000)
    def aliases_for_work(self, workid):
        w = mb.get_work_by_id(workid, includes=["aliases"])
        w = w["work"]
        ret = []
        for alias in w.get("alias-list", []):
            ret.append(alias["alias"])
        return list(set(ret))

    def match(self, a, b):
        if isinstance(a, unicode):
            a = unidecode.unidecode(a)
        if isinstance(b, unicode):
            b = unidecode.unidecode(b)
        bey = re.compile(r'\bbey\b')
        efendi = re.compile(r'\befendi\b')
        a = a.lower()
        b = b.lower()

        # Remove bey and efendi honorifics
        a = bey.sub("", a)
        b = bey.sub("", b)
        a = efendi.sub("", a)
        b = efendi.sub("", b)

        # lowercase and remove all non-letters (spaces, ', -, etc)
        a = re.sub(r"[^a-z]", "", a)
        b = re.sub(r"[^a-z]", "", b)

        # if a match, return
        if a == b:
            return True

        # otherwise, do edit distance.
        # an edit of <= 3 at the end of a string counts as a match
        if len(a) > len(b):
            a, b = b, a
        # now, a is the shorter one. If a starts in b at position 0
        #  then we have the overlap at the end
        if b.startswith(a):
            return True

        # Otherwise, chop both strings to the length of the shortest
        # one, and check lev distance between them for <= 3
        b = b[:len(a)]
        return Levenshtein.distance(a, b) <= 3

    def test_file(self, fname):
        fname = os.path.basename(fname)
        fname = os.path.splitext(fname)[0]
        parts = fname.split("--")
        if len(parts) != 5:
            print("wrong number of parts", parts)
            return
        makam, form, usul, name, composer = parts
        composer = composer.replace("_", " ")

        if not name:
            name = makam + ' ' + form

        name = name.replace("_", " ")
        works = mb.search_works(name)["work-list"]
        for w in works:
            for a in w.get("artist-relation-list", []):
                a = a["artist"]
                aname = a["name"]
                wname = w["title"]
                #if isinstance(aname, unicode):
                #    aname = unidecode.unidecode(aname)
                #if isinstance(wname, unicode):
                #    wname = unidecode.unidecode(wname)
                anywork = self.match(name, wname)
                anyname = self.match(composer, aname)
                reclist = self.recordingids_for_work(w["id"])
                for n in self.aliases_for_artist(a["id"]):
                    anyname = anyname or self.match(composer, n)
                for r in reclist:
                    for n in self.get_performance_credit_for_recording(r):
                        anyname = anyname or self.match(composer, n)
                for w in self.aliases_for_work(w["id"]):
                    print("matching a work alias", w)
                    anywork = anywork or self.match(name, w)
                if anywork and anyname:
                    print("  match: %s by %s - http://musicbrainz.org/work/%s" % (w["title"], aname, w["id"]))
                    self.save_scores(fname, reclist)

    @functools32.lru_cache(2000)
    def recordingids_for_work(self, workid):
        work = mb.get_work_by_id(workid, includes=["recording-rels"])
        work = work["work"]
        ret = []
        for rel in work.get("recording-relation-list", []):
            recid = rel["target"]
            ret.append(recid)
        return ret

    def test_dir(self, dirname):
        for i, f in enumerate(os.listdir(dirname)):
            print(i, f)
            fname = os.path.join(dirname, f)
            self.test_file(fname)

def main(args):
    m = MakamScore(args.s, args.p, args.m, args.a)
    if args.f:
        m.test_file(args.f)
    else:
        m.test_dir(args.s)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-s", help="symbtr txt")
    p.add_argument("-p", help="symbtr pdf")
    p.add_argument("-m", help="symbtr mid")
    p.add_argument("-a", help="audio files")
    p.add_argument("-f", help="a single file to test")
    args = p.parse_args()
    main(args)
