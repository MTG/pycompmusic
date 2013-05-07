#!/usr/bin/python

import sys
import os
import argparse
import collections
import unidecode
import shutil

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
        for root, dirs, files in os.walk(source_dir):
            if len(files):
                for f in files:
                    if compmusic.file.is_mp3_file(f):
                        fname = os.path.join(root, f)
                        metadata = compmusic.file.file_metadata(fname)
                        recordingid = metadata["meta"]["recordingid"]
                        if recordingid:
                            self.mapping[recordingid].append(fname)

    def save_scores(self, fname, workid):
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

        work = mb.get_work_by_id(workid, includes=["recording-rels"])
        work = work["work"]
        for rel in work.get("recording-relation-list", []):
            recid = rel["target"]
            for fname in self.mapping.get(recid, []):
                if os.path.exists(os.path.join(target, os.path.basename(fname))):
                    name = os.path.basename(fname)
                    sourcedir = os.path.dirname(fname)
                    n, ext = os.path.splitext(name)
                    newname = n + "_1" + ext
                    newdest = os.path.join(target, newname)
                    print name, "exists, copying", target, "to", newname, "instead"
                    shutil.copy(fname, newdest)
                else:
                    shutil.copy(fname, target)

    def match(self, a, b):
        if isinstance(a, unicode):
            a = unidecode.unidecode(a)
        if isinstance(b, unicode):
            b = unidecode.unidecode(b)
        import re
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
            if len(b) - len(a) <= 3:
                return True

        # otherwise, lev dand listance of <= 3
        import Levenshtein
        return Levenshtein.distance(a, b) <= 3

    def test_file(self, fname):
        fname = os.path.basename(fname)
        fname = os.path.splitext(fname)[0]
        parts = fname.split("--")
        if len(parts) != 5:
            print "wrong number of parts", parts
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
                if isinstance(aname, unicode):
                    aname = unidecode.unidecode(aname)
                if isinstance(wname, unicode):
                    wname = unidecode.unidecode(wname)
                if self.match(composer, aname) and self.match(name, wname):
                    print "  match: %s by %s - http://musicbrainz.org/work/%s" % (w["title"], aname, w["id"])
                    self.save_scores(fname, w["id"])

    def test_dir(self, dirname):
        for i, f in enumerate(os.listdir(dirname)):
            print i, f
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
