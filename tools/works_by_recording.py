import sys
import os
import argparse
import collections
import unidecode
import shutil
import json
import codecs

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

def copy_recordingid_to_dir(recordingid):
    files = recording_to_file.get(recordingid, [])
    for fname in files:
        name = os.path.basename(fname)
        n, ext = os.path.splitext(name)
        if os.path.exists(os.path.join(TARGET_DIR, n)):
            sourcedir = os.path.dirname(fname)
            rand = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
            ndir = "%s_%s" % (n, rand)
            newname = "%s%s" % (ndir, ext)
            newdest = os.path.join(TARGET_DIR, ndir, newname)
            try:
                os.makedirs(os.path.dirname(newdest))
            except:
                pass
            print name, "exists, copying", target, "to", newname, "instead"
            shutil.copy(fname, newdest)
        else:
            innertarget = os.path.join(TARGET_DIR, n)
            try:
                os.makedirs(innertarget)
            except:
                pass
            shutil.copy(fname, innertarget)

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
            copy_recordingid_to_dir(e)
            output.write(u'<li><a href="http://musicbrainz.org/recording/%s">%s</a></li>\n' % (e, recordingnames[e]))
        output.write("</ul>")
    output.write("</ul></body></html>")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-c", help="collection id")
    args = p.parse_args()
    if not os.path.exists("works_by_recording.json"):
        main(args.c)
    dump_data()
