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

import sys
import os
import argparse
import collections
import unidecode
import shutil
import json
import codecs
import random
import string

import compmusic.musicbrainz
import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

if os.path.exists("recording_to_file.json"):
    recording_to_file = json.load(open("recording_to_file.json"))
else:
    recording_to_file = {}

TARGET_DIR = "audio"

def copy_recordingid_to_dir(recordingid, workname, recordingname):
    files = recording_to_file.get(recordingid, [])
    if not files:
        return False
    target = os.path.join(TARGET_DIR, workname, recordingname)
    for fname in files:
        name = os.path.basename(fname)
        n, ext = os.path.splitext(name)
        if os.path.exists(target):
            rand = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
            newdest = "%s_%s" % (target, rand)
            newname = "%s_%s%s" % (n, rand, ext)
            try:
                os.makedirs(newdest)
            except:
                raise
                pass
            print name, "exists, copying", fname, "to", newdest, "instead"
            shutil.copy(fname, os.path.join(newdest, newname))
        else:
            try:
                os.makedirs(target)
            except:
                pass
            shutil.copy(fname, target)
    return True

def main(collectionid):
    # work -> list recordings
    mapping = collections.defaultdict(list)
    # map from an id to a name
    recordingnames = {}
    worknames = {}
    for i, releaseid in enumerate(compmusic.musicbrainz.get_releases_in_collection(collectionid)):
        print i, releaseid
        try:
            rel = mb.get_release_by_id(releaseid, includes=["recordings"])
        except:
            continue
        rel = rel["release"]

        for medium in rel.get("medium-list", []):
            for track in medium.get("track-list", []):
                recid = track["recording"]["id"]
                recordingnames[recid] = track["recording"]["title"]
                recording = mb.get_recording_by_id(recid, includes=["work-rels"])
                recording = recording["recording"]
                for work in recording.get("work-relation-list", []):
                    workid = work["work"]["id"]
                    worknames[workid] = work["work"]["title"]
                    mapping[workid].append(recid)

    data = []
    for k, v in mapping.items():
        data.append((k, v))
    data = sorted(data, key=lambda x: len(x[1]), reverse=True)
    all_d = {"recordingnames": recordingnames,
            "worknames": worknames,
            "data": data
            }
    json.dump(all_d, open("works_by_recording.json", "w"))

def dump_data():
    all_d = json.load(open("works_by_recording.json"))
    data = all_d["data"]
    data = sorted(data, key=lambda x: len(x[1]), reverse=True)
    worknames = all_d["worknames"]
    recordingnames = all_d["recordingnames"]
    output = codecs.open("works.html", "w","utf8")
    output.write("<html><head>")
    output.write('<meta charset="utf-8">\n')
    output.write("<title>Works</title></head><body>\n")
    output.write("<ul>\n")
    for d in data:
        i = d[0]
        output.write(u'<li><a href="http://musicbrainz.org/work/%s">%s</a></li>\n' % (i, worknames[i]))
        output.write("<ul>")
        for e in d[1]:
            is_file = copy_recordingid_to_dir(e, worknames[i], recordingnames[e])
            bit = " *" if not is_file else ""
            output.write(u'<li><a href="http://musicbrainz.org/recording/%s">%s%s</a></li>\n' % (e, recordingnames[e], bit))
        output.write("</ul>")
    output.write("</ul></body></html>")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-c", help="collection id")
    args = p.parse_args()
    if not os.path.exists("works_by_recording.json"):
        main(args.c)
    dump_data()
