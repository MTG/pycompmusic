#!/usr/bin/env python
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

import compmusic.file
import compmusic.musicbrainz
import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(False)
mb.set_hostname("sitar.s.upf.edu:8090")

import eyed3
import logging
eyed3.utils.log.log.setLevel(logging.ERROR)

class Stats(object):

    # How many recordings are done for each work
    # key is workid
    work_recording_counts = collections.Counter()

    # artists. could be artists of the release, or as release
    # rels, or as track rels
    artists = set()
    # releases
    releases = set()
    # recordings
    recordings = set()
    # distinct works
    works = set()
    # composers of works
    composers = set()
    # lyricicsts of works
    lyricists = set()

    def stats_for_recording(self, recordingid):
        """ Given a recording id, get its work (if it exists) and
            the composer and lyricist of the work """
        self.recordings.add(recordingid)
        recording = mb.get_recording_by_id(recordingid, includes=["work-rels", "artist-rels"]) 
        recording = recording["recording"]
        for relation in recording.get("artist-relation-list", []):
            artist = relation.get("artist", {}).get("id")
            if artist:
                self.artists.add(artist)

        for relation in recording.get("work-relation-list", []):
            workid = relation.get("work", {}).get("id")
            self.works.add(workid)
            self.work_recording_counts[workid] += 1
            work = mb.get_work_by_id(workid, includes=["artist-rels"])
            work = work["work"]
            for artist in work.get("artist-relation-list", []):
                t = artist["type"]
                aid = artist.get("artist", {}).get("id")
                if aid:
                    if t == "composer":
                        self.composers.add(aid)
                    elif t == "lyricist":
                        self.lyricists.add(aid)

    def stats_for_release(self, releaseid):
        self.releases.add(releaseid)
        rel = mb.get_release_by_id(releaseid, includes=["recordings", "artist-rels"])
        rel = rel["release"]
        for disc in rel["medium-list"]:
            for track in disc["track-list"]:
                recording = track["recording"]["id"]
                self.stats_for_recording(recording)
        for relation in rel.get("artist-relation-list", []):
            artist = relation.get("artist", {}).get("id")
            if artist:
                self.artists.add(artist)

    def print_stats(self):
        print("releases", len(self.releases))
        print("recordings", len(self.recordings))
        print("works", len(self.works))
        print("artists", len(self.artists))
        print("composers", len(self.composers))
        print("lyricists", len(self.lyricists))
        rev = collections.Counter()
        for k, v in self.work_recording_counts.items():
            rev[v] += 1
        print("recordings-per-work counts")
        print(rev)

def duration_of_release(releasedir):
    duration = 0
    for fname in os.listdir(releasedir):
        fpath = os.path.join(releasedir, fname)
        if compmusic.file.is_mp3_file(fpath):
            meta = compmusic.file.file_metadata(fpath)
            duration += meta["duration"]
    return duration

def format_seconds(secs):
    seconds = secs % 60
    minutes = (secs / 60) % 60
    hours = secs / 60 / 60
    ret = ""
    if hours > 0:
        ret += "%d:" % hours
    ret += "%d:%d" % (minutes, seconds)
    return ret

def main(collectionid, colldir):
    duration = 0

    num_releases = 0
    for root, dirs, files in os.walk(colldir):
        if len(files):
            num_releases += 1
            duration += duration_of_release(root)
    print(num_releases, "total releases")
    print("duration", format_seconds(duration))

    stats = Stats()
    for i, release in enumerate(compmusic.musicbrainz.get_releases_in_collection(collectionid)):
        print(i, release)
        try:
            stats.stats_for_release(release)
        except mb.ResponseError as e:
            print("  error when loading this release")
    stats.print_stats()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("col", help="MBID of the collection")
    p.add_argument("dir", help="Directory to get stats from")
    args = p.parse_args()
    if args.col and args.dir:
        main(args.col, args.dir)
